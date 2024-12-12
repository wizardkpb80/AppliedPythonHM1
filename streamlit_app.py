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
    results = run_async(weather_api.get_multiple_current_temperatures, cities)
    return results

# Get current temperature for multiple cities synchronously
cities = ["Berlin", "Cairo", "Dubai", "Beijing", "Moscow"]
results = process_temperature_data(cities)
temperature_data = TemperatureData(cities=list(seasonal_temperatures.keys()))
data = temperature_data.generate_realistic_temperature_data(num_years=10)

season_stats = temperature_data.calculate_seasonal_statistics(data)

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

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write("Загруженные данные:", df.head())

    # Статистика по данным
    st.write("Описательная статистика по данным:")
    st.write(df.describe())

    # Визуализация временного ряда температур
    st.write("Временной ряд температур для выбранного города:")
    city_data = df[df['city'] == city]
    plt.figure(figsize=(10, 6))
    plt.plot(city_data['timestamp'], city_data['temperature'], label='Температура')
    plt.title(f"Временной ряд температур для города {city}")
    plt.xlabel("Дата")
    plt.ylabel("Температура (°C)")
    plt.xticks(rotation=45)
    plt.legend()
    st.pyplot()

    # Сезонные профили
    season_stats = temperature_data.calculate_seasonal_statistics(df)
    city_season_stats = season_stats[season_stats['city'] == city]
    st.write(f"Сезонные профили для города {city}:")
    st.write(city_season_stats)

    # Проверка текущей температуры
    if api_key:
        current_temp = get_current_temperature(city, api_key)
        if current_temp is not None:
            current_season = month_to_season[datetime.now().month]
            is_normal = temperature_data.is_temperature_normal(city, current_temp, season_stats, current_season)
            if is_normal:
                st.success(f"Текущая температура в {city}: {current_temp}°C. Она в пределах нормы для текущего сезона.")
            else:
                st.error(f"Текущая температура в {city}: {current_temp}°C. Это аномальная температура для текущего сезона.")
else:
    st.warning("Введите API-ключ для получения текущей температуры.")

