from flask import Flask, jsonify, request
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

# Database Connection
DB_PARAMS = {
    'dbname':   'weatherdb',
    'user':     'postgres',
    'password': '6980368134Aa!',
    'host':     'localhost',
    'port':     5432,
}

def get_conn():
    return psycopg2.connect(**DB_PARAMS, cursor_factory=RealDictCursor)

# 1) List locations
@app.route('/locations', methods=['GET'])
def list_locations():
    """
    Returns a list of unique locations (lat/lon) from raw_data.parsed_forecasts.
    """
    sql = """
      SELECT DISTINCT
        location_lat AS lat,
        location_lon AS lon
      FROM raw_data.parsed_forecasts
      ORDER BY lat, lon;
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()
    return jsonify(rows)


# 2) Latest forecast per location per day
@app.route('/forecast/latest', methods=['GET'])
def latest_per_day():
    """
    For each location and each forecast_date, return the latest entry
    (i.e. highest retrieved_at) for each parameter.
    """
    sql = """
    WITH ranked AS (
      SELECT
        location_lat, location_lon,
        parameter, forecast_date, value, retrieved_at,
        ROW_NUMBER() OVER (
          PARTITION BY location_lat, location_lon, parameter, forecast_date
          ORDER BY retrieved_at DESC
        ) AS rn
      FROM raw_data.parsed_forecasts
    )
    SELECT
      location_lat, location_lon,
      parameter, forecast_date, value, retrieved_at
    FROM ranked
    WHERE rn = 1
    ORDER BY location_lat, location_lon, forecast_date, parameter;
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()
    return jsonify(rows)


#3) Average temperature of last 3 forecasts per location per day
@app.route('/forecast/average_temp', methods=['GET'])
def average_temp_last3():
    """
    Calculate average t_2m:C over the last 3 retrieved_at entries
    for each location and forecast_date.
    """
    sql = """
    WITH filtered AS (
      SELECT
        location_lat, location_lon,
        forecast_date, value AS temperature,
        ROW_NUMBER() OVER (
          PARTITION BY location_lat, location_lon, forecast_date
          ORDER BY retrieved_at DESC
        ) AS rn
      FROM raw_data.parsed_forecasts
      WHERE parameter = 't_2m:C'
    )
    SELECT
      location_lat, location_lon,
      forecast_date,
      ROUND(AVG(temperature)::numeric, 2) AS avg_temp_last3
    FROM filtered
    WHERE rn <= 3
    GROUP BY location_lat, location_lon, forecast_date
    ORDER BY location_lat, location_lon, forecast_date;
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()
    return jsonify(rows)


# 4) Top N locations by metric
@app.route('/locations/top', methods=['GET'])
def top_locations():
    """
    Return the top N locations ordered by the latest average value
    of a chosen parameter (e.g. t_2m:C, wind_speed_10m:ms).
    Query params:
      - parameter: name of metric (default: t_2m:C)
      - n: number of locations (default: 3)
    """
    param    = request.args.get('parameter', 't_2m:C')
    n        = request.args.get('n',3, type=int)

    sql = f"""
    WITH latest AS (
      SELECT
        location_lat, location_lon,
        value,
        ROW_NUMBER() OVER (
          PARTITION BY location_lat, location_lon
          ORDER BY forecast_date DESC, retrieved_at DESC
        ) AS rn
      FROM raw_data.parsed_forecasts
      WHERE parameter = %s
    )
    SELECT
      location_lat, location_lon,
      value AS latest_value
    FROM latest
    WHERE rn = 1
    ORDER BY latest_value DESC
    LIMIT %s;
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, (param, n))
        rows = cur.fetchall()
    return jsonify(rows)


# Run the app 
if __name__ == '__main__':
    app.run(debug=True, port=5000)