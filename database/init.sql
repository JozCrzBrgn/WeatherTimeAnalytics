-- Create a database for weather data
CREATE DATABASE db_weather;

-- Connect to db_weather and grant permissions
\c db_weather;
GRANT ALL PRIVILEGES ON DATABASE db_weather TO db_weather_user;
GRANT ALL PRIVILEGES ON SCHEMA public TO db_weather_user;

-- Create a database for Airflow metadata
CREATE DATABASE airflow_db;

-- Connect to airflow_db and grant permissions
\c airflow_db;
GRANT ALL PRIVILEGES ON DATABASE airflow_db TO db_weather_user;
GRANT ALL PRIVILEGES ON SCHEMA public TO db_weather_user;