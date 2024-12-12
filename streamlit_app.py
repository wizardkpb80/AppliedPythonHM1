import streamlit as st
from utils import time_decorator_sync
from weather import WeatherAPI
from temperature_data import TemperatureData, seasonal_temperatures, month_to_season
from utils import run_async
import datetime
import matplotlib.pyplot as plt

API_KEY = st.secrets["API_KEY"]
# Initialize WeatherAPI and TemperatureData
weather_api = WeatherAPI(API_KEY)
temperature_data = TemperatureData(cities=["Berlin", "Cairo", "Dubai", "Beijing", "Moscow"])

@time_decorator_sync  # Synchronous decorator applied
def get_current_temperature_sync(city):
    return weather_api.get_current_temperature(city)

temperature_data = TemperatureData(cities=list(seasonal_temperatures.keys()))
data = temperature_data.generate_realistic_temperature_data(num_years=10)

season_stats = temperature_data.calculate_seasonal_statistics(data)

# Основной интерфейс
st.title("Анализ Температурных Данных")
st.sidebar.header("Настройки")

# Выбор города
city = st.sidebar.selectbox("Выберите город", seasonal_temperatures.keys())

# Ввод API-ключа
api_key = st.sidebar.text_input("Введите ваш API-ключ OpenWeatherMap")

# Инициализация данных
temperature_data = TemperatureData(list(seasonal_temperatures.keys()))

if data is not None:
    st.write("Загруженные данные:", data.head())

    # Статистика по данным
    st.write("Описательная статистика по данным:")
    st.write(data.describe())

    # Visualizing the temperature time series
    st.write("Временной ряд температур для выбранного города:")
    
    # Filter the data for the selected city
    city_data = data[data['city'] == city]
    
    # Create the figure and axis explicitly
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot the temperature data
    ax.plot(city_data['timestamp'], city_data['temperature'], label='Температура')
    ax.set_title(f"Временной ряд температур для города {city}")
    ax.set_xlabel("Дата")
    ax.set_ylabel("Температура (°C)")
    ax.tick_params(axis='x', rotation=45)
    ax.legend()

# Display the plot
st.pyplot(fig)
    # Сезонные профили
    season_stats = temperature_data.calculate_seasonal_statistics(data)
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

