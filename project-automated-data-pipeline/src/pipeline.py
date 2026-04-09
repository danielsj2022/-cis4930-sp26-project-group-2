import json
import os
from datetime import datetime
import sqlite3
import requests
import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry


def main():
    multiple_city_weather_report = api_extract()

    df = transform_to_dataframe(multiple_city_weather_report)  
    
    save_to_csv(df)
    save_to_sqlite(df)
    
# Try and a mix up block
# The except block
def api_extract() -> dict[str, dict[str, any]]:
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    locations = [
        (30.4383, -84.2807, "tallahassee"),   
        (32.7831, -96.8067, "dallas"),   
        (40.7143, -74.006, "New York")      
    ]
    url = "https://api.open-meteo.com/v1/forecast"
    cities_forecast = {}

    for lat, lon, city in locations:
        params = {
            "latitude": lat,
            "longitude": lon,
            "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_probability_max"],
            "hourly": "temperature_2m",
            "current": "temperature_2m",
            "timezone": "America/New_York",
            "wind_speed_unit": "mph",
            "temperature_unit": "fahrenheit",
            "precipitation_unit": "inch",
            # "per_page": 5,    open-meteo does not use pagination
            # "page": 1
        }
        try:
            response = retry_session.get(url, params=params, timeout=10)
            print(f"{city} status code: {response.status_code}")

            response.raise_for_status()
            data = response.json()

            record = {
                "city": city,
                "current_temp": data.get("current", {}).get("temperature_2m", -999),
                "seven_days": data.get("daily", {}).get("time", []),
                "seven_day_hourly_temp": data.get("hourly", {}).get("temperature_2m", []),
                "seven_day_daily_temp_max": data.get("daily", {}).get("temperature_2m_max", []),
                "seven_day_daily_temp_min": data.get("daily", {}).get("temperature_2m_min", []),
                "seven_day_precipitation_probability": data.get("daily", {}).get("precipitation_probability_max", [])
            }

            cities_forecast[city] = record

        except requests.exceptions.Timeout:
            print(f"Request timed out for {city}. Skipping this city.")

        except requests.exceptions.RequestException as e:
            print(f"Request error for {city}: {e}")

        except ValueError:
            print(f"JSON decoding failed for {city}. Skipping this city.")

    return cities_forecast
    

def transform_to_dataframe(data): 
        return pd.DataFrame.from_dict(data, orient='index')

def save_to_csv(df):    
    os.makedirs("data/processed", exist_ok=True)
    file_path = "data/processed/7day_weather.csv"

    if os.path.exists(file_path):
        df.to_csv(file_path, mode='a', header=False, index=False)
    else:
        df.to_csv(file_path, index=False)

    print("7-day data saved.")

def save_to_sqlite(df):
    os.makedirs("data/processed", exist_ok=True)
    db_path = "data/processed/weather_data.db"
    conn = sqlite3.connect(db_path)

    df["seven_days"] = df["seven_days"].apply(lambda x: str(x)) # Convert list to string for SQLite storage
    df["seven_day_hourly_temp"] = df["seven_day_hourly_temp"].apply(lambda x: str(x))
    df["seven_day_daily_temp_max"] = df["seven_day_daily_temp_max"].apply(lambda x: str(x))
    df["seven_day_daily_temp_min"] = df["seven_day_daily_temp_min"].apply(lambda x: str(x))
    df["seven_day_precipitation_probability"] = df["seven_day_precipitation_probability"].apply(lambda x: str(x))

    df.to_sql(
        "weather",
        conn,
        if_exists="append",
        index=False
    )

    # cursor = conn.cursor()
    # cursor.execute("SELECT * FROM weather")
    # rows = cursor.fetchall()
    # print("from db")
    # for r in rows:
    #     print(r)

    conn.close()
    print(f"Saved {len(df)} rows to SQLite.")

if __name__ == "__main__":
    main()

    
