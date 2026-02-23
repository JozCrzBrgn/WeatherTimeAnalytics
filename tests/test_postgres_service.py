from unittest.mock import MagicMock, patch

import pytest
from psycopg2 import Error, connect

from api.insert_data import connect_to_db, create_table
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


# * --------------------------- *#
# * ------ create_table ------ *#
# * --------------------------- *#
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
            port="5433",  # Todo: cnf.postgres.port,
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