import requests
from os import getenv
from dotenv import load_dotenv
from datetime import datetime, timedelta
import time
import pandas as pd

load_dotenv()

AVIATIONSTACK_API_KEY = getenv("AVIATIONSTACK_API_KEY")
AVIATIONSTACK_API_URL = "http://api.aviationstack.com/v1/flights"

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
OPEN_METEO_HISTORY_URL = "https://archive-api.open-meteo.com/v1/archive"
GEOCODING_API_URL = "https://geocoding-api.open-meteo.com/v1/search"

weather_cache = {}


def get_flights():
    url = f"http://api.aviationstack.com/v1/flights?access_key={AVIATIONSTACK_API_KEY}&limit=10"
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
        if not departure.get("airport") or not arrival.get("airport"):
            continue  # Skip flights with missing airport info

        flights.append({
            "flight_number": flight.get("flight", {}).get("iata", "Unknown"),
            "departure_airport": departure.get("airport"),
            "arrival_airport": arrival.get("airport"),
            "departure_time": departure.get("estimated", "Unknown")  # ISO format time
        })

    return flights


def get_coordinates(location_name):
    if location_name in weather_cache:
        return weather_cache[location_name]['lat'], weather_cache[location_name]['lon']

    url = f"{GEOCODING_API_URL}?name={location_name}&count=1"
    response = requests.get(url)
    data = response.json()
    print('request for coordinates sent')
    if "results" in data and len(data["results"]) > 0:
        lat, lon = data["results"][0]["latitude"], data["results"][0]["longitude"]
        weather_cache[location_name] = {'lat': lat, 'lon': lon}
        return lat, lon
    else:
        print(f"Could not find coordinates for {location_name}")
        return None, None


# Step 3: Fetch current and forecast weather from Open-Meteo (cache results)
def get_weather(location_name):
    if location_name in weather_cache and 'weather' in weather_cache[location_name]:
        return weather_cache[location_name]['weather']

    lat, lon = get_coordinates(location_name)
    if lat is None or lon is None:
        return None  # Skip if location not found

    url = f"{OPEN_METEO_URL}?latitude={lat}&longitude={lon}&current_weather=true&hourly=temperature_2m,precipitation,wind_speed_10m"
    response = requests.get(url)
    data = response.json()
    print('request for weather sent')
    # Cache weather data for future use
    if 'current_weather' in data:
        weather_cache[location_name]['weather'] = data
    return data


# Step 4: Fetch historical weather for 10 years (3-hour intervals)
def get_historical_weather(location_name, date):
    if location_name in weather_cache and 'historical' in weather_cache[location_name]:
        return weather_cache[location_name]['historical']

    lat, lon = get_coordinates(location_name)
    if lat is None or lon is None:
        return None  # Skip if location not found

    historical_data = []
    for year in range(10):  # Go back 10 years
        date_clean = date.split("+")[0]  # Keeps only the part before '+'
        past_date = (datetime.strptime(date_clean, "%Y-%m-%dT%H:%M:%S") - timedelta(days=365 * year)).strftime("%Y-%m-%d")
        url = f"{OPEN_METEO_HISTORY_URL}?latitude={lat}&longitude={lon}&start_date={past_date}&end_date={past_date}&hourly=temperature_2m,precipitation,wind_speed_10m"
        response = requests.get(url)
        data = response.json()
        print('request for historical weather sent')
        if "hourly" in data:
            historical_data.append({
                "date": past_date,
                "temperature": data["hourly"]["temperature_2m"][0],  # Take first 3-hour interval
                "precipitation": data["hourly"]["precipitation"][0],
                "wind_speed": data["hourly"]["wind_speed_10m"][0]
            })

    # Cache historical data for future use
    weather_cache[location_name]['historical'] = historical_data
    return historical_data


def process_flights():
    flights = get_flights()
    results = []

    for flight in flights:
        dep_weather = get_weather(flight["departure_airport"])
        arr_weather = get_weather(flight["arrival_airport"])

        # Get historical weather (10 years, 3-hour intervals)
        historical_dep = get_historical_weather(flight["departure_airport"], flight["departure_time"])
        historical_arr = get_historical_weather(flight["arrival_airport"], flight["departure_time"])

        results.append({
            "flight_number": flight["flight_number"],
            "departure_airport": flight["departure_airport"],
            "arrival_airport": flight["arrival_airport"],
            "departure_time": flight["departure_time"],
            "departure_weather": dep_weather["current_weather"] if dep_weather and "current_weather" in dep_weather else None,
            "arrival_weather": arr_weather["current_weather"] if arr_weather and "current_weather" in arr_weather else None,
            "historical_departure_weather": historical_dep,
            "historical_arrival_weather": historical_arr
        })

        time.sleep(1)  # Avoid API rate limits

    return results

# Step 5: Run and Save to CSV
flights_data = process_flights()
df = pd.DataFrame(flights_data)
df.to_csv("flights_weather_data.csv", index=False)

print("Data saved to flights_weather_data.csv")