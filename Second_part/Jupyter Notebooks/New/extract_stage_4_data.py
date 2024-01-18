month = 8
year = 2022
folder = "oluwa33823"



import os
import pandas as pd
import numpy as np
import pygrib
from datetime import datetime

# Folder path
folder_path = f'C:/Users/omitu/Documents/GitHub/Urbanization-and-Climate-Change/Second_part/data/precip/{folder}'
save_path = f'C:/Users/omitu/Documents/GitHub/Urbanization-and-Climate-Change/Second_part/data/precip'

# List all GRIB2 files in the folder
files = [f for f in os.listdir(folder_path) if f.endswith('.grb2')]

# Initialize an empty DataFrame to hold all data
all_data = pd.DataFrame()

for file in files:
    file_path = os.path.join(folder_path, file)

    # Extracting date and time from the filename
    date_str = file.split('.')[1]  # Extracts '2021062719'
    date_time = datetime.strptime(date_str, '%Y%m%d%H')  # Converts to datetime object

    # Read the GRIB2 file
    grbs = pygrib.open(file_path)
    grb = grbs.select()[0]  # Assuming the first record contains the precipitation data
    precipitation, lats, lon = grb.data(lat1=29, lat2=31, lon1=-95.3, lon2=-93.95)

    # Flatten the arrays
    lats_flat = np.ravel(lats)
    lon_flat = np.ravel(lon)
    precipitation_flat = np.ravel(precipitation.data)

    # Create a DataFrame for this file
    df = pd.DataFrame({
        'Longitude': lon_flat,
        'Latitude': lats_flat,
        'Precipitation': precipitation_flat
    })

    # Filter out rows where precipitation data is masked
    df = df[~precipitation.mask.ravel()]

    # Add the date and time
    df['Date_Time'] = date_time

    # Append this DataFrame to the all_data DataFrame
    all_data = pd.concat([all_data, df], ignore_index=True)

# Save dataset
all_data.to_csv(os.path.join(save_path, f'Precip_{month}_{year}.csv'))