import pandas as pd
import numpy as np

# Sample temperature data for cities
seasonal_temperatures = {
    "New York": {"winter": 0, "spring": 10, "summer": 25, "autumn": 15},
    "London": {"winter": 5, "spring": 11, "summer": 18, "autumn": 12},
    "Paris": {"winter": 4, "spring": 12, "summer": 20, "autumn": 13},
    "Tokyo": {"winter": 6, "spring": 15, "summer": 27, "autumn": 18},
    "Moscow": {"winter": -10, "spring": 5, "summer": 18, "autumn": 8},
    "Sydney": {"winter": 12, "spring": 18, "summer": 25, "autumn": 20},
    "Berlin": {"winter": 0, "spring": 10, "summer": 20, "autumn": 11},
    "Beijing": {"winter": -2, "spring": 13, "summer": 27, "autumn": 16},
    "Rio de Janeiro": {"winter": 20, "spring": 25, "summer": 30, "autumn": 25},
    "Dubai": {"winter": 20, "spring": 30, "summer": 40, "autumn": 30},
    "Los Angeles": {"winter": 15, "spring": 18, "summer": 25, "autumn": 20},
    "Singapore": {"winter": 27, "spring": 28, "summer": 28, "autumn": 27},
    "Mumbai": {"winter": 25, "spring": 30, "summer": 35, "autumn": 30},
    "Cairo": {"winter": 15, "spring": 25, "summer": 35, "autumn": 25},
    "Mexico City": {"winter": 12, "spring": 18, "summer": 20, "autumn": 15},
}

month_to_season = {12: "winter", 1: "winter", 2: "winter",
                   3: "spring", 4: "spring", 5: "spring",
                   6: "summer", 7: "summer", 8: "summer",
                   9: "autumn", 10: "autumn", 11: "autumn"}

class TemperatureData:
    def __init__(self, cities):
        self.cities = cities

    def generate_realistic_temperature_data(self, num_years=10):
        dates = pd.date_range(start="2010-01-01", periods=365 * num_years, freq="D")
        data = []

        for city in self.cities:
            for date in dates:
                season = month_to_season[date.month]
                mean_temp = seasonal_temperatures[city][season]
                # Adding random variation
                temperature = np.random.normal(loc=mean_temp, scale=5)
                data.append({"city": city, "timestamp": date, "temperature": temperature})

        df = pd.DataFrame(data)
        df['season'] = df['timestamp'].dt.month.map(lambda x: month_to_season[x])

        return df

    def calculate_seasonal_statistics(self, data):
        season_stats = data.groupby(['city', 'season'])['temperature'].agg(['mean', 'std']).reset_index()
        season_stats = season_stats.rename(columns={'mean': 'season_mean', 'std': 'season_std'})
        return season_stats

    def is_temperature_normal(self, city, current_temp, season_stats, current_season):
        city_season_stats = season_stats[(season_stats['city'] == city) & (season_stats['season'] == current_season)]
        print(city_season_stats.describe())
        if city_season_stats.empty:
            return None  # No data for comparison
        mean = city_season_stats['season_mean'].values[0]
        std = city_season_stats['season_std'].values[0]
        lower_bound = mean - 2 * std
        upper_bound = mean + 2 * std
        return lower_bound <= current_temp <= upper_bound

    def load_data(self, file):
        """
        Загрузить данные из файла, проверив наличие необходимых колонок.
        """
        try:
            data = pd.read_csv(file)
            # Проверка наличия необходимых столбцов
            required_columns = {'city', 'timestamp', 'temperature'}
            if not required_columns.issubset(data.columns):
                raise ValueError(f"Файл должен содержать столбцы: {', '.join(required_columns)}")

            # Преобразование timestamp в формат datetime
            data['timestamp'] = pd.to_datetime(data['timestamp'], errors='coerce')
            if data['timestamp'].isna().any():
                raise ValueError("Некорректные значения в колонке 'timestamp'. Убедитесь, что даты записаны правильно.")

            # Добавление колонки с сезонами
            data['season'] = data['timestamp'].dt.month.map(lambda x: month_to_season[x])

            return data

        except Exception as e:
            raise ValueError(f"Ошибка при загрузке файла: {e}")


