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