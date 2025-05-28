CREATE SCHEMA IF NOT EXISTS raw_data

-- this table stores json response as it is extracted from the api
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
