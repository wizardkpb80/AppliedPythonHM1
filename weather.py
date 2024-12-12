import requests
import aiohttp
import asyncio
from utils import time_decorator

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

class WeatherAPI:
    def __init__(self, api_key):
        self.api_key = api_key

    def get_current_temperature(self, city):
        params = {
            "q": city,
            "appid": self.api_key,
            "units": "metric"  # Use Celsius
        }
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        return data['main']['temp']

    @time_decorator
    async def get_current_temperature_async(self, city, session):
        params = {
            "q": city,
            "appid": self.api_key,
            "units": "metric"
        }
        async with session.get(BASE_URL, params=params) as response:
            data = await response.json()
            return city, data['main']['temp']

    @time_decorator
    async def get_multiple_current_temperatures(self, cities):
        async with aiohttp.ClientSession() as session:
            tasks = [self.get_current_temperature_async(city, session) for city in cities]
            results = await asyncio.gather(*tasks)
            return {city: temp for city, temp in results}
