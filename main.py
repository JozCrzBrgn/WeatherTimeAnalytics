import logging

from api.api_requests import build_weather_url, mock_fetch_data
from api.insert_data import connect_to_db

if __name__ == "__main__":
    conn = None
    try:
        url = build_weather_url("New York")
        # data = fetch_data(url)
        data = mock_fetch_data("New York", 1)
        conn = connect_to_db()
        print(conn)
    except:
        logging.error("ETL execution failed", exc_info=True)
    finally:
        if conn:
            conn.close()
            logging.info("Database connection closed")
