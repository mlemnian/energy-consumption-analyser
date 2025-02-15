import json
import pandas as pd
from datetime import datetime
# pip install matplotlib
import matplotlib.pyplot as plt
import numpy as np

def readJson(file_path: str):
    with open(file_path, 'r') as file:
        json_data = json.load(file)
    
    return json_data


def readCsv(file_path: str):
    csv_data = pd.read_csv(file_path, skiprows=2, sep=';')
    return csv_data


def convertTicksToDate(tick_value: int) -> str:
    # Convert ticks to a datetime object
    date_time = datetime.fromtimestamp(tick_value / 1000.0)

    # Format the datetime object into a readable string
    formatted_date = date_time.strftime('%d')
    return formatted_date


def getCategories(series):
    return [convertTicksToDate(item[0]) for item in series]


def getValues(series):
    return np.array([item[1] for item in series])


data = readJson('2025_01.json')

wp_data = readCsv('energy_data_2025.csv')

wp_heating_values = [item[1]/1000.0 for item in wp_data.values[:31]]
wp_water_values = [item[2]/1000.0 for item in wp_data.values[:31]]

batterySeries = data['settings']['series'][0]['data']
directSeries = data['settings']['series'][1]['data']
externalSeries = data['settings']['series'][2]['data']

categories = getCategories(batterySeries)
battery_values = getValues(batterySeries)
direct_values = getValues(directSeries)
external_values = getValues(externalSeries)

# Create the bar plot
plt.bar(categories, direct_values, label='Direkt Verbrauch', color='yellow')
plt.bar(categories, battery_values, bottom=direct_values, label='Baterie Verbrauch', color='green')
plt.bar(categories, external_values, bottom=(battery_values + direct_values), label='Externer Verbrauch', color='grey')
plt.plot(categories, wp_heating_values, label='WP Heizung Verbrauch', color='blue')
plt.plot(categories, wp_water_values, label='WP Warmwasser Verbrauch', color='red')

plt.legend()

# Add labels and title
plt.xlabel('Days')
plt.ylabel('kWh')
plt.title('Stromverbrauch im Januar 2025')

# Show the plot
plt.show()
