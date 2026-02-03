# WeatherDB Data Pipeline

A data engineering pipeline that ingests meteorological data from the Meteomatics API, stores raw JSON payloads in PostgreSQL, and transforms the data into a structured schema for analysis.

## Project Overview

This application demonstrates a robust **ELT (Extract, Load, Transform)** workflow. It is designed to handle hierarchical weather data by PostgreSQL's native JSONB capabilities.

**Key Features:**
* **Ingestion:** Fetches complex weather data via the Meteomatics API.
* **Raw Storage:** Stores exact API responses into a `raw_forecasts` table (JSONB) to ensure data lineage and recoverability.
* **Transformation:** Uses SQL (`CROSS JOIN LATERAL`) to flatten nested JSON structures into a tabular `parsed_forecasts` format.
* **API Layer:** Provides a Flask REST endpoint to serve the processed data.

## 🛠 Tech Stack

* **Language:** Python 3.x
* **Framework:** Flask
* **Database:** PostgreSQL (using JSONB data types)
* **API:** Meteomatics Weather API

## ⚙️ Local Setup Instructions

### 1. Prerequisites
Ensure you have the following installed:
* Python 3.8+
* PostgreSQL
* Git

### 2. Clone the Repository
```bash
git clone [https://github.com/SuperPanda4/weatherdb.git](https://github.com/SuperPanda4/weatherdb.git)
cd weather_api
```

### 3. Environment Setup
Create and activate a virtual environment to manage dependencies.

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
pip install -r requirements.txt

### 5. DB Configuration
5.1. Open your terminal or SQL tool (like pgAdmin or psql).

5.2. Create the database:
<pre>
CREATE DATABASE weatherdb;
</pre>

5.3. Run the schema creation script provided in weatherdb.sql.

<pre>
INSERT INTO raw_data.parsed_forecasts 
    (location_lat, location_lon, parameter, forecast_date, value, retrieved_at)
SELECT 
    (coord_elem ->> 'lat')::NUMERIC,
    (coord_elem ->> 'lon')::NUMERIC,
    data_elem ->> 'parameter',
    (date_elem ->> 'date')::TIMESTAMP,
    (date_elem ->> 'value')::NUMERIC,
    rf.retrieved_at
FROM raw_data.raw_forecasts AS rf
    CROSS JOIN LATERAL jsonb_array_elements(rf.json_data -> 'data') AS data_elem
    CROSS JOIN LATERAL jsonb_array_elements(data_elem -> 'coordinates') AS coord_elem
    CROSS JOIN LATERAL jsonb_array_elements(coord_elem -> 'dates') AS date_elem;
</pre>


### 6. Run the APP
```
python app.py
```

The API server will start locally. You can access the endpoints at:

Base URL: http://localhost:5000
Locations Endpoint: http://localhost:5000/locations
