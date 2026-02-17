from unittest.mock import MagicMock, patch

import pytest
from psycopg2 import Error

from api.insert_data import connect_to_db

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
