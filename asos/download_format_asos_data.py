import requests
import pandas as pd
import os


year = 2022   # Change for each year

os.mkdir(f'./{year}')

stations = ['72242712975', '72059400188', '72243612906', '72242953910', 
            '72243012960', '72063700223', '72254312977', '72244012918', 
            '99848199999']

for i, station in enumerate(stations, start=1):
    url = f'https://www.ncei.noaa.gov/data/global-hourly/access/{year}/{station}.csv'
    response = requests.get(url)
    
    # Save the file
    with open(f'{station}.csv', 'wb') as f:
        f.write(response.content)

    df = pd.read_csv(f'{station}.csv')
    df['Date'] = pd.to_datetime(df['DATE'])
    df['Month'] = df['Date'].dt.month
    summer_data = df[(df['Month'] >= 3) & (df['Month'] <= 8)]
    subsetted_data = summer_data.iloc[:, [1, 3, 4, 5, 10, 11, 12, 13, 14, 15]]

    # ... continue your processing here...
    # Split the 'WND' column into 'DIR', 'DIR_QC', 'TYPE', 'SPD', 'SPD_QC' columns
    subsetted_data[['DIR', 'DIR_QC', 'WIND_TYPE', 'SPD', 'SPD_QC']] = subsetted_data['WND'].str.split(',', expand=True)

    # Split the 'CIG' column into 'HEIGHT_AGL', 'HEIGHT_QC', 'UNNECESSARY_1', 'UNNECESSARY_2'
    subsetted_data[['HEIGHT_AGL', 'HEIGHT_QC', 'UNNECESSARY_1', 'UNNECESSARY_2']] = subsetted_data['CIG'].str.split(',', expand=True)

    # Split the 'VIS' column into 'VIS', 'VIS_QC', 'Unused1', 'Unused2' columns
    subsetted_data[['VIS', 'VIS_QC', 'Unused1', 'Unused2']] = subsetted_data['VIS'].str.split(',', expand=True)

    subsetted_data[['TMP', 'TMP_QC']] = subsetted_data['TMP'].str.split(',', expand=True)
    subsetted_data[['DEW', 'DEW_QC']] = subsetted_data['DEW'].str.split(',', expand=True)
    subsetted_data[['SLP', 'SLP_QC']] = subsetted_data['SLP'].str.split(',', expand=True)

    # Remove the 'WND' column
    subsetted_data.drop('WND', axis=1, inplace=True)
    subsetted_data.drop('CIG', axis=1, inplace=True)

    # Process direction based on direction quality code
    subsetted_data.loc[subsetted_data['DIR_QC'].isin(['2', '3', '6', '7']), 'DIR'] = '999'
    subsetted_data.drop('DIR_QC', axis=1, inplace=True)

    # Process speed based on speed quality code
    subsetted_data.loc[subsetted_data['SPD_QC'].isin(['2', '3', '6', '7']), 'SPD'] = '999'
    subsetted_data.drop('SPD_QC', axis=1, inplace=True)
    subsetted_data.drop('WIND_TYPE', axis=1, inplace=True)
    subsetted_data.drop('UNNECESSARY_1', axis=1, inplace=True)
    subsetted_data.drop('UNNECESSARY_2', axis=1, inplace=True)

    # Process height AGL based on height quality code
    subsetted_data.loc[subsetted_data['HEIGHT_QC'].isin(['2', '3', '6', '7']), 'HEIGHT_AGL'] = '99999'
    subsetted_data.drop('HEIGHT_QC', axis=1, inplace=True)

    # Process visibility based on visibility quality code
    subsetted_data.loc[subsetted_data['VIS_QC'].isin(['2', '3', '6', '7']), 'VIS'] = '999999'
    subsetted_data.drop('VIS_QC', axis=1, inplace=True)
    subsetted_data.drop('Unused1', axis=1, inplace=True)
    subsetted_data.drop('Unused2', axis=1, inplace=True)

    subsetted_data.loc[subsetted_data['TMP_QC'].isin(['2', '3', '6', '7']), 'TMP'] = '9999'
    subsetted_data.drop('TMP_QC', axis=1, inplace=True)
    subsetted_data['TMP'] = pd.to_numeric(subsetted_data['TMP'], errors='coerce') / 10


    subsetted_data.loc[subsetted_data['DEW_QC'].isin(['2', '3', '6', '7']), 'DEW'] = '9999'
    subsetted_data.drop('DEW_QC', axis=1, inplace=True)
    subsetted_data['DEW'] = pd.to_numeric(subsetted_data['DEW'], errors='coerce') / 10


    subsetted_data.loc[subsetted_data['SLP_QC'].isin(['2', '3', '6', '7']), 'SLP'] = '99999'
    subsetted_data.drop('SLP_QC', axis=1, inplace=True)

    subsetted_data.to_csv(f'{year}/station{i}_{year}.csv', index=False)
    os.remove(f'{station}.csv')  # remove the original downloaded data
