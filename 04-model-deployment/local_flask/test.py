import requests
import argparse

ride = {
    "PULocationID": 10,
    "DOLocationID": 50,
    "trip_distance": 20 
}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query a prediction endpoint.")
    parser.add_argument("-url", type=str, default="http://0.0.0.0:2024/predict", help="prediction endpoint")
    args = parser.parse_args()
    
    url = args.url

    resp = requests.post(url, json=ride)
    print(resp.json())