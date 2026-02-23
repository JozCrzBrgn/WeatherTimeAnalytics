from unittest.mock import MagicMock, patch

import pytest
from psycopg2 import Error, connect

from api.api_requests import mock_fetch_data
from api.insert_data import connect_to_db, create_table, insert_weather_records
from core.config import get_settings

cnf = get_settings()

# * --------------------------- *#
# * ------ connect_to_db ------ *#
# * --------------------------- *#
@patch("api.insert_data.connect")
@patch("api.insert_data.logging")
def test_connect_to_db_success(mock_logging, mock_connect):
    """
    Successful connection test
    """
    # Arrange
    fake_conn = MagicMock()
    mock_connect.return_value = fake_conn
    # Act
    result = connect_to_db()
    # Assert
    assert result == fake_conn
    mock_connect.assert_called_once()
    mock_logging.info.assert_called_once_with("Connected to Postgres")


@patch("api.insert_data.connect")
@patch("api.insert_data.logging")
def test_connect_to_db_failure(mock_logging, mock_connect):
    # Arrange
    mock_connect.side_effect = Error("Connection failed")
    # Act & Assert
    with pytest.raises(Error):
        connect_to_db()
    mock_logging.error.assert_called_once()


# * -------------------------- *#
# * ------ create_table ------ *#
# * -------------------------- *#
def test_create_table_success():
    """
    Successful create table test
    """
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    create_table(mock_conn)
    mock_conn.cursor.assert_called_once()
    mock_cursor.execute.assert_called_once()
    mock_conn.commit.assert_called_once()


def test_create_table_failure():
    """
    Create table test error
    """
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.execute.side_effect = Error("DB error")
    with pytest.raises(Error):
        create_table(mock_conn)
    # Must have tried to create a cursor
    mock_conn.cursor.assert_called_once()
    # Do not commit if it fails
    mock_conn.commit.assert_not_called()


def test_create_table_integration():
    """
    schema and table verification test
    """
    conn = connect(
            host="localhost",  # Todo: cnf.postgres.host,
            port="5432",  # Todo: cnf.postgres.port,
            dbname="postgres",  # Todo: cnf.postgres.dbname,
            user=cnf.postgres.user,
            password=cnf.postgres.password,
        )
    create_table(conn)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'dev'
        AND table_name = 'raw_weather_data';
    """)
    result = cursor.fetchone()
    assert result is not None
    conn.close()


# * ------------------------------------ *#
# * ------ insert_weather_records ------ *#
# * ------------------------------------ *#
def test_insert_weather_records_success():
    """
    Successful insert test
    """
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    sample_weather_data = mock_fetch_data("New York", 1)
    insert_weather_records(mock_conn, sample_weather_data)

    mock_cursor.execute.assert_called_once()
    mock_conn.commit.assert_called_once()
    mock_conn.rollback.assert_not_called()


def test_insert_weather_records_params():
    """
    Validate that the parameters are correct
    """
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    sample_weather_data = mock_fetch_data("New York", 1)
    insert_weather_records(mock_conn, sample_weather_data)

    args, kwargs = mock_cursor.execute.call_args
    query_passed, params_passed = args

    assert sample_weather_data["location"]["name"] in params_passed
    assert sample_weather_data["location"]["region"] in params_passed
    assert sample_weather_data["location"]["country"] in params_passed
    assert sample_weather_data["location"]["lat"] in params_passed
    assert sample_weather_data["location"]["lon"] in params_passed
    assert sample_weather_data["location"]["timezone_id"] in params_passed
    assert sample_weather_data["current"]["temperature"] in params_passed
    assert sample_weather_data["current"]["weather_descriptions"][0] in params_passed
    assert sample_weather_data["current"]["astro"]["sunrise"] in params_passed
    assert sample_weather_data["current"]["astro"]["sunset"] in params_passed
    assert sample_weather_data["current"]["astro"]["moonrise"] in params_passed
    assert sample_weather_data["current"]["astro"]["moonset"] in params_passed
    assert sample_weather_data["current"]["air_quality"]["co"] in params_passed
    assert sample_weather_data["current"]["air_quality"]["no2"] in params_passed
    assert sample_weather_data["current"]["air_quality"]["o3"] in params_passed
    assert sample_weather_data["current"]["air_quality"]["so2"] in params_passed
    assert sample_weather_data["current"]["air_quality"]["pm2_5"] in params_passed
    assert sample_weather_data["current"]["air_quality"]["pm10"] in params_passed
    assert sample_weather_data["current"]["air_quality"]["us-epa-index"] in params_passed
    assert sample_weather_data["current"]["air_quality"]["gb-defra-index"] in params_passed
    assert sample_weather_data["current"]["pressure"] in params_passed
    assert sample_weather_data["current"]["precip"] in params_passed
    assert sample_weather_data["current"]["humidity"] in params_passed
    assert sample_weather_data["current"]["visibility"] in params_passed
    assert sample_weather_data["current"]["uv_index"] in params_passed
    assert sample_weather_data["current"]["wind_speed"] in params_passed
    assert sample_weather_data["location"]["localtime"] in params_passed
    assert sample_weather_data["location"]["utc_offset"] in params_passed


def test_insert_weather_records_failure():
    """
    Error test → rollback
    """
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    mock_cursor.execute.side_effect = Error("DB failure")

    with pytest.raises(Error):
        sample_weather_data = mock_fetch_data("New York", 1)
        insert_weather_records(mock_conn, sample_weather_data)

    mock_conn.rollback.assert_called_once()
    mock_conn.commit.assert_not_called()


def test_insert_query_contains_table():
    """
    Test of query contains correct INSERT
    """
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    sample_weather_data = mock_fetch_data("New York", 1)
    insert_weather_records(mock_conn, sample_weather_data)

    query_passed = mock_cursor.execute.call_args[0][0]
    assert "INSERT INTO dev.raw_weather_data" in query_passed