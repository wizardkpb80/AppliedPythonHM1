import streamlit as st
from utils import time_decorator_sync
from weather import WeatherAPI
from temperature_data import TemperatureData, seasonal_temperatures, month_to_season
from utils import run_async
from datetime import datetime
import matplotlib.pyplot as plt

#API_KEY = st.secrets["API_KEY"]

# Initialize WeatherAPI and TemperatureData
weather_api = WeatherAPI(API_KEY)
temperature_data = TemperatureData(list(seasonal_temperatures.keys()))
data = temperature_data.generate_realistic_temperature_data(num_years=10)

# Основной интерфейс
st.title("Анализ Температурных Данных")
st.sidebar.header("Настройки")

st.sidebar.info("Загрузите CSV-файл с колонками: city, timestamp, temperature")
uploaded_file = st.sidebar.file_uploader("Загрузите файл с историческими данными", type=["csv"])
if uploaded_file is not None:
    data = temperature_data.load_data(uploaded_file)
# Выбор города
city = st.sidebar.selectbox("Выберите город", seasonal_temperatures.keys())

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
st.pyplot(fig)

season_stats = city_data.groupby(['city', 'season'])['temperature'].agg(['mean', 'std']).reset_index()
season_stats = season_stats.rename(columns={'mean': 'season_mean', 'std': 'season_std'})
city_data = city_data.merge(season_stats, on=['city', 'season'], how='left')
city_data['is_anomaly'] = abs(city_data['temperature'] - city_data['season_mean']) > 2 * city_data['season_std']

fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(city_data['timestamp'], city_data['temperature'], label='Температура')
anomalies = city_data[city_data['is_anomaly']]
ax.scatter(anomalies['timestamp'], anomalies['temperature'], color='red', label='Аномалии')
ax.set_title(f"Временной ряд температур для города {city}")
ax.set_xlabel("Дата")
ax.set_ylabel("Температура (°C)")
ax.legend()
st.pyplot(fig)

# Сезонные профили
temperature_season_stats = temperature_data.calculate_seasonal_statistics(data)
temperature_season_stats = season_stats[season_stats['city'] == city]
st.write(f"Сезонные профили для города {city}:")
st.write(temperature_season_stats)

try:
    current_temp = weather_api.get_current_temperature(city)
    if current_temp is not None:
        current_season = month_to_season[datetime.now().month]
        is_normal = temperature_data.is_temperature_normal(city, current_temp, season_stats, current_season)
        if is_normal:
            st.success(f"Текущая температура в {city}: {current_temp}°C. Она в пределах нормы для текущего сезона.")
        else:
            st.error(f"Текущая температура в {city}: {current_temp}°C. Это аномальная температура для текущего сезона.")
except Exception as e:
    st.error(f"Ошибка weather_api: {e}")
