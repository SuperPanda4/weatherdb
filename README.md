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
Open your terminal or SQL tool (like pgAdmin or psql).

Create the database:
<pre>
CREATE DATABASE weatherdb;
</pre>
