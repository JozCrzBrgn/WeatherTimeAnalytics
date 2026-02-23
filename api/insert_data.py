import logging

from psycopg2 import Error, connect
from psycopg2.extensions import connection

from core.config import get_settings

cnf = get_settings()

def connect_to_db() -> connection:
    """
    Creates and returns a PostgreSQL database connection.

    Returns:
        connection: Active database connection.

    Raises:
        Error: If connection fails.
    """
    try:
        conn = connect(
            host="localhost",  # Todo: cnf.postgres.host,
            port="5433",  # Todo: cnf.postgres.port,
            dbname="postgres",  # Todo: cnf.postgres.dbname,
            user=cnf.postgres.user,
            password=cnf.postgres.password,
        )
        logging.info("Connected to Postgres")
        return conn
    except Error as e:
        logging.error(f"Database connection failed: {e}", exc_info=True)
        raise


def create_table(conn) -> None:
    """
    Create required schemas and the raw weather table in PostgreSQL.

    This function ensures the existence of the following schemas:
    - dev
    - stage
    - mart

    It also creates the table `dev.raw_weather_data` if it does not exist.
    The transaction is committed upon success.

    Args:
        conn: An active psycopg2 database connection object.

    Raises:
        psycopg2.Error: If the schema or table creation fails. The connection
        is closed before re-raising the exception.
    """
    try:
        cursor = conn.cursor()
        query = """
            CREATE SCHEMA IF NOT EXISTS dev;
            CREATE SCHEMA IF NOT EXISTS stage;
            CREATE SCHEMA IF NOT EXISTS mart;
            CREATE TABLE IF NOT EXISTS dev.raw_weather_data(
                id SERIAL PRIMARY KEY,
                city TEXT,
                region TEXT,
                country TEXT,
                latitude FLOAT,
                longitude FLOAT,
                timezone_id TEXT,
                temperature FLOAT,
                weather_descriptions TEXT,
                sunrise TEXT,
                sunset TEXT,
                moonrise TEXT,
                moonset TEXT,
                co FLOAT,
                no2 FLOAT,
                o3 FLOAT,
                so2 FLOAT,
                pm2_5 FLOAT,
                pm10 FLOAT,
                us_epa_index INT,
                gb_defra_index INT,
                pressure FLOAT,
                precipitation FLOAT,
                humidity FLOAT,
                visibility FLOAT,
                uv_index FLOAT,
                wind_speed FLOAT,
                time TIMESTAMP,
                inserted_at TIMESTAMP DEFAULT NOW(),
                utc_offset TEXT
            );
        """
        cursor.execute(query)
        conn.commit()
        logging.info("Successfully created table")
    except Error as e:
        logging.error(f"Failed to create table: {e}", exc_info=True)
        raise


def insert_weather_records(conn, data):
    """
    Insert weather data records into the raw_weather_data table.

    Args:
        conn: An active psycopg2 database connection object.
        data (dict): The weather data dictionary returned from the API.

    Raises:
        psycopg2.Error: If the database insertion fails. The transaction
            is rolled back before re-raising the exception.
        KeyError: If the expected keys are missing from the data dictionary.
            This indicates an API response format change.
        TypeError: If the data types don't match the expected structure.
    """
    # Getting data
    location = data["location"]
    current = data["current"]
    astro = current["astro"]
    air_quality = current["air_quality"]
    # creating the query
    query = """
        INSERT INTO dev.raw_weather_data (
            city,
            region,
            country,
            latitude,
            longitude,
            timezone_id,
            temperature,
            weather_descriptions,
            sunrise,
            sunset,
            moonrise,
            moonset,
            co,
            no2,
            o3,
            so2,
            pm2_5,
            pm10,
            us_epa_index,
            gb_defra_index,
            pressure,
            precipitation,
            humidity,
            visibility,
            uv_index,
            wind_speed,
            time,
            inserted_at,
            utc_offset
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), %s)
    """
    # Loading parameters
    params = (
        location["name"],
        location["region"],
        location["country"],
        location["lat"],
        location["lon"],
        location["timezone_id"],
        current["temperature"],
        current["weather_descriptions"][0],
        astro["sunrise"],
        astro["sunset"],
        astro["moonrise"],
        astro["moonset"],
        air_quality["co"],
        air_quality["no2"],
        air_quality["o3"],
        air_quality["so2"],
        air_quality["pm2_5"],
        air_quality["pm10"],
        air_quality["us-epa-index"],
        air_quality["gb-defra-index"],
        current["pressure"],
        current["precip"],
        current["humidity"],
        current["visibility"],
        current["uv_index"],
        current["wind_speed"],
        location["localtime"],
        location["utc_offset"],
    )
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
        conn.commit()
        logging.info("Weather data inserted")
    except Error as e:
        conn.rollback()
        logging.error(f"Failed to insert weather data {e}", exc_info=True)
        raise