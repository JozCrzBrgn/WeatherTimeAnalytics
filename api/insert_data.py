import logging

from psycopg2 import Error, connect
from psycopg2.extensions import connection

from core.config import cnf


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
