from api.api_requests import build_weather_url, mock_fetch_data

if __name__ == "__main__":
    url = build_weather_url("New York")
    # data = fetch_data(url)
    data = mock_fetch_data("New York", 1)
