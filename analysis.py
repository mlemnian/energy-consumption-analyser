import json
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import os
from collections import OrderedDict


def readJson(file_path: str):
    with open(file_path, 'r') as file:
        json_data = json.load(file)
    
    return json_data


def readCsv(directory_path, year, month, filename):
    file_path = os.path.join(directory_path, year, filename)
    csv_data = pd.read_csv(file_path, skiprows=2, sep=';')
    csv_data = [item for item in csv_data.values if item[0].startswith(f'{year}-{month}')]
    return csv_data


def convertTicksToDate(tick_value: int) -> str:
    # Convert ticks to a datetime object
    date_time = datetime.fromtimestamp(tick_value / 1000.0)
    # Format the datetime object into a readable string
    formatted_date = date_time.strftime('%d')
    return formatted_date


def getCategories(min_time, max_time, tick_interval):
    series = list(range(min_time, max_time + tick_interval, tick_interval))
    return [convertTicksToDate(item) for item in series]


def getValues(series, min_time, max_time, tick_interval):
    # Create an ordered dictionary
    ordered_dict = OrderedDict()
    y_values = list(range(min_time, max_time + tick_interval, tick_interval))
    for key in y_values:
        ordered_dict[key] = 0
    
    for item in series:
        ordered_dict[item[0]] = item[1]

    return np.array(list(ordered_dict.values()))


def getValueFromWpHeatingData(wp_data, min_time, max_time, tick_interval):
    # Create an ordered dictionary
    ordered_dict = OrderedDict()
    y_values = list(range(min_time, max_time + tick_interval, tick_interval))
    for key in y_values:
        ordered_dict[convertTicksToDate(key)] = 0
    
    for item in wp_data:
        ordered_dict[item[0].split(' ')[0].split('-')[2]] = item[1]/1000.0

    return np.array(list(ordered_dict.values()))


def getValueFromWpWaterData(wp_data, min_time, max_time, tick_interval):
    # Create an ordered dictionary
    ordered_dict = OrderedDict()
    y_values = list(range(min_time, max_time + tick_interval, tick_interval))
    for key in y_values:
        ordered_dict[convertTicksToDate(key)] = 0
    
    for item in wp_data:
        ordered_dict[item[0].split(' ')[0].split('-')[2]] = item[2]/1000.0

    return np.array(list(ordered_dict.values()))


def render_plot(series_categories, direct_values, battery_values, external_values, 
                wp_heating_categories, wp_heating_values, 
                wp_water_categories, wp_water_values, title:str):
    # Create the bar plot
    plt.bar(series_categories, direct_values, label='Direkt Verbrauch', color='yellow')
    plt.bar(series_categories, battery_values, bottom=direct_values, label='Batterie Verbrauch', color='green')
    plt.bar(series_categories, external_values, bottom=(battery_values + direct_values), label='Externer Verbrauch', color='grey')
    plt.plot(wp_heating_categories, wp_heating_values, label='WP Heizung Verbrauch', color='blue')
    plt.plot(wp_water_categories, wp_water_values, label='WP Warmwasser Verbrauch', color='red')

    plt.legend()

    # Add labels and title
    plt.xlabel('Days')
    plt.ylabel('kWh')
    plt.title(title)

    # Show the plot
    plt.savefig(fname=title)
    plt.close()


def process(directory_path, year, json_file:str):
    month = json_file.split('.')[0]
    json_file_path = os.path.join(directory_path, year, json_file)
    print(json_file_path)
    pv_data = readJson(os.path.join(json_file_path))

    min_time = int(pv_data['settings']['xAxis']['min'])
    max_time = int(pv_data['settings']['xAxis']['max'])
    tick_interval = int(pv_data['settings']['xAxis']['tickInterval'])
    battery_series = pv_data['settings']['series'][0]['data']
    direct_series = pv_data['settings']['series'][1]['data']
    external_series = pv_data['settings']['series'][2]['data']

    
    series_categories = getCategories(min_time, max_time, tick_interval)
    direct_values = getValues(direct_series, min_time, max_time, tick_interval)
    battery_values = getValues(battery_series, min_time, max_time, tick_interval)
    external_values = getValues(external_series, min_time, max_time, tick_interval)

    wp_data = readCsv(directory_path, year, month, 'wp_energy_data.csv')

    wp_heating_categories = getCategories(min_time, max_time, tick_interval)
    wp_heating_values = getValueFromWpHeatingData(wp_data, min_time, max_time, tick_interval)

    wp_water_categories = getCategories(min_time, max_time, tick_interval)
    wp_water_values = getValueFromWpWaterData(wp_data, min_time, max_time, tick_interval)
    
    title = f'Stromverbrauch_im_{month}_{year}'
    render_plot(series_categories,
                direct_values, battery_values, external_values, 
                wp_heating_categories, wp_heating_values, 
                wp_water_categories, wp_water_values, title)


def main():
    directory_path = './data'
    for year in os.listdir(directory_path):
        year_path = os.path.join(directory_path, year)
        if os.path.isdir(year_path):
            monthly_json_files = [f for f in os.listdir(year_path) if f.endswith('.json')]
            for json_file in monthly_json_files:
                process(directory_path, year, json_file)


if __name__ == "__main__":
    main()
