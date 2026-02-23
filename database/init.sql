-- Create a database for weather data
CREATE DATABASE db_weather;

-- Connect to db_weather and grant permissions
\c db_weather;
GRANT ALL PRIVILEGES ON DATABASE db_weather TO db_weather_user;
GRANT ALL PRIVILEGES ON SCHEMA public TO db_weather_user;