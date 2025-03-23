import time
from datetime import datetime, timedelta, timezone
from os import getenv

import pandas as pd
import requests
from dotenv import load_dotenv
from joblib import dump

from airport_location import get_airport_coordinates


load_dotenv()

AVIATIONSTACK_API_KEY = getenv("AVIATIONSTACK_API_KEY")
AVIATIONSTACK_API_URL = "http://api.aviationstack.com/v1/flights"

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
OPEN_METEO_HISTORY_URL = "https://archive-api.open-meteo.com/v1/archive"

FLIGHTS_AMOUNT = 100000  # Number of flights to fetch


def get_flights():
    url = f"http://api.aviationstack.com/v1/flights?access_key={AVIATIONSTACK_API_KEY}&limit={FLIGHTS_AMOUNT}"
    response = requests.get(url)
    data = response.json()
    print('request for flights sent')

    if "data" not in data:
        print("Error fetching flights:", data)
        return []

    flights = []
    for flight in data["data"]:
        departure = flight.get("departure", {})
        arrival = flight.get("arrival", {})

        # Ensure required data exists
        if not departure.get("airport") or not arrival.get("airport") or not arrival.get('actual'):
            continue  # Skip flights with missing airport info

        flights.append({
            "flight_number": flight.get("flight", {}).get("iata", "Unknown"),
            "flight_status": flight.get("flight_status", "Unknown"),
            "departure_airport": departure.get("airport"),
            "arrival_airport": arrival.get("airport"),
            "departure_airport_iata": departure.get("iata"),
            "arrival_airport_iata": arrival.get("iata"),
            "scheduled_departure_time": departure.get("scheduled", "Unknown"),  # ISO format time
            "scheduled_arrival_time": arrival.get("scheduled", "Unknown"),  # ISO format time
            "actual_departure_time": departure.get("actual", None),  # ISO format time
            "actual_arrival_time": arrival.get("actual", None)  # ISO format time
        })
    return flights


def get_weather(flight_time, lat, lon):
    """
    Получает погоду за 3 часа до и после заданного времени в указанной локации.
    """
    weather_data = {}  # Словарь для хранения данных по каждому году

    flight_dt = datetime.fromisoformat(flight_time)  # Преобразуем ISO8601 время в объект datetime
    start_time = (flight_dt - timedelta(hours=3)).strftime("%Y-%m-%dT%H:%M:%S")
    end_time = (flight_dt + timedelta(hours=3)).strftime("%Y-%m-%dT%H:%M:%S")

    # Выбираем нужный API (архивный или прогнозный)
    is_past = flight_dt < datetime.now(timezone.utc)
    base_url = OPEN_METEO_HISTORY_URL if is_past else OPEN_METEO_URL

    url = (
        f"{base_url}?latitude={lat}&longitude={lon}"
        f"&start_date={start_time[:10]}&end_date={end_time[:10]}"
        f"&hourly=temperature_2m,rain,snowfall,snow_depth,showers,visibility,wind_speed_180m,temperature_180m"
    )

    response = requests.get(url)
    data = response.json()
    weather_data = []

    if 'hourly' in data:
        df = pd.DataFrame(data['hourly'])
        weather_data.append(df)

    for year in range(1, 6):  # Цикл на 5 лет назад
        past_dt = flight_dt - timedelta(days=365 * year)  # Вычитаем год
        start_time = (past_dt - timedelta(hours=3)).strftime("%Y-%m-%dT%H:%M:%S")
        end_time = (past_dt + timedelta(hours=3)).strftime("%Y-%m-%dT%H:%M:%S")

        url = (
            f"{OPEN_METEO_HISTORY_URL}?latitude={lat}&longitude={lon}"
            f"&start_date={start_time[:10]}&end_date={end_time[:10]}"
            f"&hourly=temperature_2m,precipitation,wind_speed_10m"
        )

        response = requests.get(url)
        data = response.json()

        if "hourly" in data:
            df = pd.DataFrame(data["hourly"])
            weather_data.append(df)
    if weather_data:
        final_df = pd.concat(weather_data, ignore_index=True)
    else:
        final_df = pd.DataFrame()
        final_df['time'] = pd.to_datetime(final_df['time'])

    return final_df


def process_flights(flights) -> list[dict, pd.DataFrame, pd.DataFrame]:
    results = []

    for flight in flights:
        lat_dep, lon_dep = get_airport_coordinates(flight["departure_airport_iata"])
        lat_arr, lon_arr = get_airport_coordinates(flight["arrival_airport_iata"])
        if flight["actual_departure_time"]:
            dep_weather = get_weather(flight["actual_departure_time"], lat_dep, lon_dep)
        else:
            dep_weather = get_weather(flight["scheduled_departure_time"], lat_dep, lon_dep)
        if flight["actual_arrival_time"]:
            arr_weather = get_weather(flight["actual_arrival_time"], lat_arr, lon_arr)
        else:
            arr_weather = get_weather(flight["scheduled_arrival_time"], lat_arr, lon_arr)
        flight_info = {
            "flight_number": flight["flight_number"],
            "flight_status": flight["flight_status"],
            'departure_airport_iata': flight["departure_airport_iata"],
            'arrival_airport_iata': flight["arrival_airport_iata"],
            "scheduled_departure_time": flight["scheduled_departure_time"],
            "scheduled_arrival_time": flight["scheduled_arrival_time"],
            "actual_departure_time": flight["actual_departure_time"],
            "actual_arrival_time": flight["actual_arrival_time"],
        }
        results.append((flight_info, dep_weather, arr_weather))
        time.sleep(1)  # Avoid API rate limits

    return results


flights = get_flights()
flights_data = process_flights(flights)

dump(flights_data, 'flights_data.joblib')  # Save data to file
