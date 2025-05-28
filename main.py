import requests
from datetime import datetime, timedelta
from requests.auth import HTTPBasicAuth
import psycopg2
from psycopg2.extras import Json
import os

USERNAME = 'norismike_sioutas_ioannis'
PASSWORD = 'c9Do8HX7ip'
DB_PARAMS = {
    'dbname':   os.environ.get('DB_NAME'),
    'user':     os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PASSWORD'),
    'host':     os.environ.get('DB_HOST'),
    'port':     os.environ.get('DB_PORT', 5432),
}

LOCATIONS = {
    "Berlin": "52.520551,13.461804",
    "Paris":  "48.8566,2.3522",
    "Rome":   "41.9028,12.4964"
}

start_date = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
end_date   = (datetime.utcnow() + timedelta(days=7)).strftime('%Y-%m-%dT%H:%M:%SZ')
interval   = 'P1D'
parameters = 't_2m:C,wind_speed_10m:ms,precip_1h:mm'
fmt        = 'json'
BASE_URL   = 'https://api.meteomatics.com'

def fetch_forecast(coords):
    url = f"{BASE_URL}/{start_date}--{end_date}:{interval}/{parameters}/{coords}/{fmt}"
    resp = requests.get(url, auth=HTTPBasicAuth(USERNAME, PASSWORD))
    resp.raise_for_status()
    return resp.json()

def store_raw_json(conn, data):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO raw_data.raw_forecasts (json_data)
            VALUES (%s)
        """, (Json(data),))
    conn.commit()

def main():
    conn = psycopg2.connect(**DB_PARAMS)

    for name, coords in LOCATIONS.items():
        print(f" Fetching {name}")
        data = fetch_forecast(coords)
        print(f" Inserting raw JSON for {name}")
        store_raw_json(conn, data)

    conn.close()
    print("All done.")

if __name__ == "__main__":
    main()
