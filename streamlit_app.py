import streamlit as st
from utils import time_decorator_sync
from weather import WeatherAPI
from temperature_data import TemperatureData, seasonal_temperatures, month_to_season
from utils import run_async
import datetime

API_KEY = st.secrets["API_KEY"]
# Initialize WeatherAPI and TemperatureData
weather_api = WeatherAPI(API_KEY)
temperature_data = TemperatureData(cities=["Berlin", "Cairo", "Dubai", "Beijing", "Moscow"])

@time_decorator_sync  # Synchronous decorator applied
def get_current_temperature_sync(city):
    return weather_api.get_current_temperature(city)

@time_decorator_sync  # Synchronous decorator applied
def process_temperature_data(cities):
#    results = run_async(weather_api.get_multiple_current_temperatures, cities)
#    return results
    tasks = [weather_api.get_current_temperature(city) for city in cities]
    return await asyncio.gather(*tasks)

# Get current temperature for multiple cities synchronously
cities = ["Berlin", "Cairo", "Dubai", "Beijing", "Moscow"]
results = process_temperature_data(cities)

# Основной интерфейс
st.title("Анализ Температурных Данных")
st.sidebar.header("Настройки")

# Загрузка исторических данных
uploaded_file = st.sidebar.file_uploader("Загрузите файл с историческими данными", type="csv")

# Выбор города
city = st.sidebar.selectbox("Выберите город", seasonal_temperatures.keys())

# Ввод API-ключа
api_key = st.sidebar.text_input("Введите ваш API-ключ OpenWeatherMap")

# Инициализация данных
temperature_data = TemperatureData(list(seasonal_temperatures.keys()))

