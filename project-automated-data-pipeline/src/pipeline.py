import requests
import pandas as pd
from retry_requests import retry
import requests_cache
from datetime import datetime
import os
import json
import sqlite3


def main():
    data = api_extract()

    save_raw_json(data)

    df = transform_to_dataframe(data)
    save_to_csv(df)
    save_to_sqlite(df)


def api_extract():
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=3, backoff_factor=0.2)

    locations = [
        (30.4383, -84.2807, "tallahassee"),
        (32.7831, -96.8067, "dallas"),
        (40.7143, -74.0060, "new york")
    ]

    url = "https://api.open-meteo.com/v1/forecast"
    results = {}

    for lat, lon, city in locations:
        params = {
            "latitude": lat,
            "longitude": lon,
            "daily": [
                "temperature_2m_max",
                "temperature_2m_min",
                "precipitation_probability_max"
            ],
            "temperature_unit": "fahrenheit",
            "timezone": "America/New_York"
        }

        try:
            response = retry_session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            results[city] = {
                "city": city,
                "dates": data.get("daily", {}).get("time", []),
                "temp_max": data.get("daily", {}).get("temperature_2m_max", []),
                "temp_min": data.get("daily", {}).get("temperature_2m_min", []),
                "precip": data.get("daily", {}).get("precipitation_probability_max", [])
            }

        except requests.exceptions.RequestException as e:
            print(f"Error for {city}: {e}")

    return results


def save_raw_json(data):
    os.makedirs("data/raw", exist_ok=True)
    filename = f"data/raw/weather_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

    print("Raw JSON saved.")


def transform_to_dataframe(data):
    rows = []

    for city, info in data.items():
        for i in range(len(info["dates"])):
            rows.append({
                "city": city,
                "date": info["dates"][i],
                "temp_max": info["temp_max"][i],
                "temp_min": info["temp_min"][i],
                "precip": info["precip"][i]
            })

    return pd.DataFrame(rows)


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

    df.to_sql(
        "weather",
        conn,
        if_exists="append",
        index=False
    )

    conn.close()

    print(f"Saved {len(df)} rows to SQLite.")


if __name__ == "__main__":
    main()

"""
    # Process 3 locations
for response in responses:
	print(f"\nCoordinates: {response.Latitude()}°N {response.Longitude()}°E")
	print(f"Elevation: {response.Elevation()} m asl")
	print(f"Timezone: {response.Timezone()}{response.TimezoneAbbreviation()}")
	print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")
	
	# Process current data. The order of variables needs to be the same as requested.
	current = response.Current()
	current_temperature_2m = current.Variables(0).Value()
	
	print(f"\nCurrent time: {current.Time()}")
	print(f"Current temperature_2m: {current_temperature_2m}")
	
	# Process hourly data. The order of variables needs to be the same as requested.
	hourly = response.Hourly()
	hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
	
	hourly_data = {"date": pd.date_range(
		start = pd.to_datetime(hourly.Time() + response.UtcOffsetSeconds(), unit = "s", utc = True),
		end =  pd.to_datetime(hourly.TimeEnd() + response.UtcOffsetSeconds(), unit = "s", utc = True),
		freq = pd.Timedelta(seconds = hourly.Interval()),
		inclusive = "left"
	)}
	
	hourly_data["temperature_2m"] = hourly_temperature_2m
	
	hourly_dataframe = pd.DataFrame(data = hourly_data)
	print("\nHourly data\n", hourly_dataframe)
	
	# Process daily data. The order of variables needs to be the same as requested.
	daily = response.Daily()
	daily_temperature_2m_max = daily.Variables(0).ValuesAsNumpy()
	daily_temperature_2m_min = daily.Variables(1).ValuesAsNumpy()
	daily_precipitation_probability_max = daily.Variables(2).ValuesAsNumpy()
	
	daily_data = {"date": pd.date_range(
		start = pd.to_datetime(daily.Time() + response.UtcOffsetSeconds(), unit = "s", utc = True),
		end =  pd.to_datetime(daily.TimeEnd() + response.UtcOffsetSeconds(), unit = "s", utc = True),
		freq = pd.Timedelta(seconds = daily.Interval()),
		inclusive = "left"
	)}
	
	daily_data["temperature_2m_max"] = daily_temperature_2m_max
	daily_data["temperature_2m_min"] = daily_temperature_2m_min
	daily_data["precipitation_probability_max"] = daily_precipitation_probability_max
	
	daily_dataframe = pd.DataFrame(data = daily_data)
	print("\nDaily data\n", daily_dataframe)
"""
