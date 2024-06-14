import requests
import argparse

query = {
    "year": 2023,
    "month": 3,
    "taxi": "green" 
}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query a prediction endpoint.")
    parser.add_argument("-url", type=str, default="http://0.0.0.0:2024/predict", help="prediction endpoint")
    args = parser.parse_args()
    
    url = args.url

    resp = requests.post(url, json=query)
    print(resp.json())