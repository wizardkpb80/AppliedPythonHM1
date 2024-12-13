from utils import time_decorator_sync
from weather import WeatherAPI
from temperature_data import TemperatureData, seasonal_temperatures, month_to_season
from utils import run_async
import datetime

API_KEY = "c2f6bec934bedd4b070444ac59ccca2a"  # Replace with your API Key

# Initialize WeatherAPI and TemperatureData
weather_api = WeatherAPI(API_KEY)
temperature_data = TemperatureData(cities=["Berlin", "Cairo", "Dubai", "Beijing", "Moscow"])

@time_decorator_sync  # Synchronous decorator applied
def get_current_temperature_sync(city):
    return weather_api.get_current_temperature(city)

@time_decorator_sync  # Synchronous decorator applied
def process_temperature_data(cities):
    results = run_async(weather_api.get_multiple_current_temperatures, cities)
    return results

# Get current temperature for multiple cities synchronously
cities = ["Berlin", "Cairo", "Dubai", "Beijing", "Moscow"]
results = process_temperature_data(cities)
temperature_data = TemperatureData(cities=list(seasonal_temperatures.keys()))
data = temperature_data.generate_realistic_temperature_data(num_years=10)

season_stats = temperature_data.calculate_seasonal_statistics(data)

# Example: Checking the temperature for Berlin
current_season = month_to_season[datetime.datetime.now().month]
current_temp = get_current_temperature_sync("Berlin")

# Checking if the current temperature is normal
is_normal = temperature_data.is_temperature_normal("Berlin", current_temp, season_stats, current_season)

if is_normal:
    print(f"Температура в Берлине ({current_temp}°C) в пределах нормы.")
else:
    print(f"Температура в Берлине ({current_temp}°C) аномальна.")

current_temp = get_current_temperature_sync("Moscow")
is_normal = temperature_data.is_temperature_normal("Moscow", current_temp, season_stats, current_season)

if is_normal:
    print(f"Температура в Москве ({current_temp}°C) в пределах нормы.")
else:
    print(f"Температура в Москве ({current_temp}°C) аномальна.")