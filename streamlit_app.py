import streamlit as st
from utils import time_decorator_sync
from weather import WeatherAPI
from temperature_data import TemperatureData, seasonal_temperatures, month_to_season
from utils import style_table
from datetime import datetime
import matplotlib.pyplot as plt

# Initialize WeatherAPI and TemperatureData

temperature_data = TemperatureData(list(seasonal_temperatures.keys()))
data = temperature_data.generate_realistic_temperature_data(num_years=10)

# Основной интерфейс
st.title("Анализ Температурных Данных")
st.sidebar.header("По умолчанию данные сгенерированы автоматически")

# Форма для ввода API-ключа
api_key = st.sidebar.text_input("Введите ваш API-ключ OpenWeatherMap:", type="password")

st.sidebar.info("Загрузите CSV-файл с колонками: city, timestamp, temperature")
uploaded_file = st.sidebar.file_uploader("Загрузите файл с историческими данными", type=["csv"])
if uploaded_file is not None:
    data = temperature_data.load_data(uploaded_file)
# Выбор города
city = st.sidebar.selectbox("Выберите город", seasonal_temperatures.keys())

st.write("### Загруженные данные:")
st.dataframe(style_table(data.head()), use_container_width=True)

# Статистика по данным
st.write("Описательная статистика по данным:")
st.write(style_table(data.describe()), use_container_width=True)

# Filter the data for the selected city
city_data = data[data['city'] == city]

# Create the figure and axis explicitly
fig, ax = plt.subplots(figsize=(10, 6))

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

# Сезонные профили
seasonal_stats = city_data[city_data['city'] == city]
fig, ax = plt.subplots(figsize=(8, 5))
ax.bar(seasonal_stats['season'], seasonal_stats['season_mean'], yerr=seasonal_stats['season_std'], capsize=5)
ax.set_title(f"Средние температуры и отклонения в {city}")
ax.set_xlabel("Сезон")
ax.set_ylabel("Температура (°C)")
st.pyplot(fig)

# Вывод данных
st.subheader("Данные")
st.dataframe(style_table(city_data[['timestamp', 'temperature', 'season', 'is_anomaly']]), use_container_width=True)

if api_key:
    try:
        weather_api = WeatherAPI(api_key)
        current_temp = weather_api.get_current_temperature(city)
        if isinstance(current_temp, dict) and "error" in current_temp:
            st.error("Ошибка: Некорректный API-ключ. Проверьте и попробуйте снова.")
        elif current_temp is not None:
            current_season = month_to_season[datetime.now().month]
            is_normal = temperature_data.is_temperature_normal(city, current_temp, season_stats, current_season)
            if is_normal:
                st.success(f"Текущая температура в {city}: {current_temp}°C. Она в пределах нормы для текущего сезона.")
            else:
                st.error(f"Текущая температура в {city}: {current_temp}°C. Это аномальная температура для текущего сезона.")
        else:
            st.error("Не удалось получить текущую температуру. Проверьте введённый API-ключ.")
    except Exception as e:
        st.error(f"Ошибка weather_api: {e}")
else:
    st.info("Введите API-ключ OpenWeatherMap для получения данных о текущей температуре.")
