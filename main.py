import json

from api.api_requests import build_weather_url, fetch_data

if __name__ == "__main__":
    url = build_weather_url("New York")
    data = fetch_data(url)
    with open('data.json', 'w') as json_file:
        json.dump(data, json_file, indent=4) 
