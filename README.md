# weatherdb
weatherdb project
This project is a simple Flask application that retrieves weather data from an external API, stores the JSON response into a PostgreSQL database, and provides an endpoint to view the stored data.

Features
Fetches and stores raw weather data

Saves data in PostgreSQL

Simple REST endpoint to access weather data

Local Setup Instructions:
1. Prerequisites

-Python 3.x
-PostgreSQL

2. Clone the Repository
git clone https://github.com/SuperPanda4/weatherdb.git
cd weather_api

3. Create and Activate a Virtual Environment
run this command ->> python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate


4. Install Dependencies
pip install -r requirements.txt

5. Set Up PostgreSQL
Open the SQL shell (psql) and run:

-> CREATE DATABASE weatherdb;
-> the rest of the creation statements can be found in the weatherdb.sql file but i am also attaching here 
CREATE TABLE if not exists raw_data.raw_forecasts (
  json_data    JSONB     NOT NULL,
  retrieved_at TIMESTAMP NOT NULL DEFAULT NOW()
);

--this table stores the parsed structured data from the previous table
CREATE TABLE if not exists raw_data.parsed_forecasts (
  location_lat   NUMERIC     NOT NULL,
  location_lon   NUMERIC     NOT NULL,
  parameter      TEXT        NOT NULL,
  forecast_date  TIMESTAMP   NOT NULL,
  value          NUMERIC     NOT NULL,
  retrieved_at   TIMESTAMP   NOT NULL
);

INSERT INTO raw_data.parsed_forecasts (location_lat, location_lon, parameter, forecast_date, value, retrieved_at)
SELECT
  (coord_elem ->> 'lat')::NUMERIC        AS location_lat,
  (coord_elem ->> 'lon')::NUMERIC        AS location_lon,
  data_elem  ->> 'parameter'             AS parameter,
  (date_elem  ->> 'date')::TIMESTAMP     AS forecast_date,
  (date_elem  ->> 'value')::NUMERIC      AS value,
  rf.retrieved_at                        AS retrieved_at
FROM raw_data.raw_forecasts AS rf
  CROSS JOIN LATERAL jsonb_array_elements(rf.json_data -> 'data')        AS data_elem
  CROSS JOIN LATERAL jsonb_array_elements(data_elem -> 'coordinates')    AS coord_elem
  CROSS JOIN LATERAL jsonb_array_elements(coord_elem -> 'dates')         AS date_elem;


Make sure the credentials in your app.py (or config file) match your local PostgreSQL setup.

6. Run the Flask App
run this command -> python app.py


The app will be available at http://localhost:5000.

Try hitting http://localhost:5000/locations to see the data.
