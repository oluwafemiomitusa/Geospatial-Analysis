from scipy.spatial import cKDTree
import numpy as np
import os
import wradlib as wrl
import pyart
import pyproj
import pandas as pd
from datetime import datetime
from numpy import ma


batch = 'third'                       # Batch of data to process
season = 'summer'

# Initialize an empty DataFrame
all_data = pd.DataFrame()

# Specify base directory and get list of folders (dates)
base_dir = f'/content/drive/My Drive/L3 Data/{season}/{batch}/'
folder_list = os.listdir(base_dir)  # get the list of folders

# Define target coordinates
latitudes = [29.717, 29.64586, 29.61667, 29.98438, 30.06801, 29.51924, 29.5, 29.61971, 29.726]
longitudes = [-95.383, -95.28212, -95.1667, -95.3607, -95.5563, -95.2423, -95.477, -95.6575, -95.266]
target_coords = list(zip(latitudes, longitudes))

# Loop over all folders
for folder in folder_list:
    # Get the list of files in the current folder
    file_list = os.listdir(base_dir + folder)

    # Loop over all data files
    for data_file in file_list:
        # Extract date and time from filename
        datetime_str = data_file.split('_')[-1]  # get 'YYYYMMDDHHMM' part
        datetime_obj = datetime.strptime(datetime_str, '%Y%m%d%H%M')

        # Complete path to the file
        aws_nexrad_level3_precip_file = base_dir + folder + '/' + data_file

        # Read the data using PyART
        radar_level3_precip = pyart.io.read_nexrad_level3(aws_nexrad_level3_precip_file)

        # Get radar gate (data point) information
        azimuths = radar_level3_precip.azimuth['data']
        ranges = radar_level3_precip.range['data']
        elevation = radar_level3_precip.elevation['data'][0]  # assuming all elevations are the same

        # Get radar location
        radar_lon = radar_level3_precip.longitude['data'][0]
        radar_lat = radar_level3_precip.latitude['data'][0]

        # Define the WGS84 ellipsoid
        wgs84 = pyproj.Proj(proj='latlong', datum='WGS84')

        # Convert (azimuth, range, elevation) to (x, y, z) in the WGS84 projection
        coords = wrl.georef.polar.spherical_to_proj(ranges, azimuths, elevation, (radar_lon, radar_lat))

        lon = coords[..., 0]
        lat = coords[..., 1]

        # Obtain precipitation data
        precip_data = radar_level3_precip.fields['radar_estimated_rain_rate']['data']

        # Apply the mask to the precipitation data
        masked_precip_data = ma.masked_array(precip_data, mask=radar_level3_precip.fields['radar_estimated_rain_rate']['data'].mask)

        # Get the precipitation values without the masked values
        precip_values = masked_precip_data.compressed()

        # Apply the mask to lon and lat arrays
        lon_masked = ma.masked_array(lon, mask=masked_precip_data.mask)
        lat_masked = ma.masked_array(lat, mask=masked_precip_data.mask)

        # Get the lon and lat values without the masked values
        lon_values = lon_masked.compressed()
        lat_values = lat_masked.compressed()

        # Create a DataFrame for this file with columns 'Date', 'Time', 'Longitude', 'Latitude', and 'Precipitation'
        data = {'DateTime': [datetime_obj]*len(lon_values),
                'Longitude': lon_values,
                'Latitude': lat_values,
                'Precipitation': precip_values}
        df = pd.DataFrame(data)

        # Add the data from this file to the combined DataFrame
        all_data = pd.concat([all_data, df])


# Set DateTime as index
all_data.set_index('DateTime', inplace=True)

# Group by hour and sum precipitation
grouped_data = all_data.groupby([pd.Grouper(freq='H'), 'Longitude', 'Latitude']).sum().reset_index()

# Create a KDTree from target coordinates
target_tree = cKDTree(target_coords)

# Create a KDTree from precipitation coordinates
precip_tree = cKDTree(grouped_data[['Latitude', 'Longitude']].values)

# Get the distance and index of the closest target coordinate for each precipitation point
distances, closest_points = target_tree.query(precip_tree.data, k=1)
closest_points = closest_points.flatten()

# Convert distances to a list
distances = distances.tolist()

# Add the closest target coordinates and distances to the DataFrame
grouped_data['Target_Latitude'] = [latitudes[i] for i in closest_points]
grouped_data['Target_Longitude'] = [longitudes[i] for i in closest_points]
grouped_data['Distance'] = distances

# Define a threshold distance (in the same units as your coordinates)
threshold_distance = 0.01  # Adjust this value as needed

# Select rows where the distance to the nearest target coordinate is below the threshold
selected_data = grouped_data[grouped_data['Distance'] < threshold_distance]

# Select the row with the minimum distance in each group
selected_data = selected_data.loc[selected_data.groupby(['DateTime', 'Target_Latitude', 'Target_Longitude'])['Distance'].idxmin()]

# Save the selected data to a CSV file
grouped_data.to_csv(f'/content/drive/My Drive/L3 Data/total_precip_{season}_{batch}.csv', index=False)
selected_data.to_csv(f'/content/drive/My Drive/L3 Data/selected_precip_{season}_{batch}.csv', index=False)

# Display the data+
print(selected_data)
