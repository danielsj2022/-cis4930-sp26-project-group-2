import requests
import pandas as pd
from retry_requests import retry
import requests_cache
from datetime import datetime
import os
import json
import sqlite3


import pandas as pd
from typing import Any, Dict
import os
import sqlite3

def main() -> None:
    multiple_city_weather_report = api_extract()
    df = transform_to_dataframe(multiple_city_weather_report)  
    
    save_to_csv(df)
    save_to_sqlite(df)


def api_extract() -> Dict[str, Dict[str, Any]]:
    ...
    return cities_forecast
    

def transform_to_dataframe(data: Dict[str, Dict[str, Any]]) -> pd.DataFrame: 
    return pd.DataFrame.from_dict(data, orient='index')


def save_to_csv(df: pd.DataFrame) -> None:    
    os.makedirs("data/processed", exist_ok=True)
    file_path = "data/processed/7day_weather.csv"

    if os.path.exists(file_path):
        df.to_csv(file_path, mode='a', header=False, index=False)
    else:
        df.to_csv(file_path, index=False)

    print("7-day data saved.")


def save_to_sqlite(df: pd.DataFrame) -> None:
    os.makedirs("data/processed", exist_ok=True)
    db_path = "data/processed/weather_data.db"
    conn = sqlite3.connect(db_path)

    df["seven_days"] = df["seven_days"].apply(lambda x: str(x))
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

    conn.close()
    print(f"Saved {len(df)} rows to SQLite.")