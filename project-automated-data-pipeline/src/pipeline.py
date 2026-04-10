import json
import os
from datetime import datetime
import sqlite3
import requests
import requests_cache
import pandas as pd
from retry_requests import retry
import logging  # ADDED: real logging

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # ADDED: makes paths work with cron
LOG_DIR = os.path.join(BASE_DIR, "logs")  # ADDED: logs folder
os.makedirs(LOG_DIR, exist_ok=True)  # ADDED: create logs folder if missing

logging.basicConfig(  # ADDED: configure logging
    filename=os.path.join(LOG_DIR, "daily_etl.log"),  # ADDED: log file path
    level=logging.INFO,  # ADDED: log info and errors
    format="%(asctime)s - %(levelname)s - %(message)s"  # ADDED: log format
)


def main():
    logging.info("Pipeline started.")  # ADDED
    multiple_city_weather_report = api_extract()

    df = transform_to_dataframe(multiple_city_weather_report)

    save_to_csv(df)
    save_to_sqlite(df)
    logging.info("Pipeline finished.")  # ADDED


def api_extract() -> dict[str, dict[str, any]]:
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)

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
        }
        try:
            response = retry_session.get(url, params=params, timeout=10)
            logging.info(f"{city} status code: {response.status_code}")  # CHANGED: log instead of print

            response.raise_for_status()
            data = response.json()

            record = {
                "city": city,
                "seven_days": data.get("daily", {}).get("time", []),
                "seven_day_daily_temp_max": data.get("daily", {}).get("temperature_2m_max", []),
                "seven_day_daily_temp_min": data.get("daily", {}).get("temperature_2m_min", []),
                "seven_day_precipitation_probability": data.get("daily", {}).get("precipitation_probability_max", [])
            }

            cities_forecast[city] = record
            logging.info(f"Successfully fetched data for {city}.")  # ADDED

        except requests.exceptions.Timeout:
            logging.error(f"Request timed out for {city}. Skipping this city.")  # CHANGED

        except requests.exceptions.RequestException as e:
            logging.error(f"Request error for {city}: {e}")  # CHANGED

        except ValueError:
            logging.error(f"JSON decoding failed for {city}. Skipping this city.")  # CHANGED

    return cities_forecast


def transform_to_dataframe(data: dict[str, dict[str, any]]) -> pd.DataFrame:
    rows = []

    for city, info in data.items():
        dates = info.get("seven_days", [])
        max_temps = info.get("seven_day_daily_temp_max", [])
        min_temps = info.get("seven_day_daily_temp_min", [])
        precip = info.get("seven_day_precipitation_probability", [])

        for i in range(len(dates)):
            rows.append({
                "city": city,
                "date": dates[i],
                "temp_max": max_temps[i],
                "temp_min": min_temps[i],
                "precip": precip[i]
            })

    return pd.DataFrame(rows)


def save_to_csv(df: pd.DataFrame) -> None:
    processed_dir = os.path.join(BASE_DIR, "data", "processed")  # CHANGED: cron-safe path
    os.makedirs(processed_dir, exist_ok=True)  # CHANGED
    file_path = os.path.join(processed_dir, "7day_weather.csv")  # CHANGED

    if os.path.exists(file_path):
        df.to_csv(file_path, mode='a', header=False, index=False)
    else:
        df.to_csv(file_path, index=False)

    logging.info(f"7-day data saved to CSV at {file_path}.")  # CHANGED


def save_to_sqlite(df: pd.DataFrame) -> None:
    processed_dir = os.path.join(BASE_DIR, "data", "processed")
    os.makedirs(processed_dir, exist_ok=True)
    db_path = os.path.join(processed_dir, "weather_data.db")
    conn = sqlite3.connect(db_path)

    df.to_sql(
        "weather",
        conn,
        if_exists="append",  # CHANGED: replaces old table schema
        index=False
    )

    conn.close()
    logging.info(f"Saved {len(df)} rows to SQLite at {db_path}.")

if __name__ == "__main__":
    main()
