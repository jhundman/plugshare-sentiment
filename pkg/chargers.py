import modal
import os
import requests
import pandas as pd
from datetime import datetime
import json
import time
from .common import stub


NUM_CHARGERS = 25000
PS_SLEEP = 1
NETWORK_NAMES = {8: "Tesla", 19: "EVgo", 47: "Electrify_America", 1: "ChargePoint"}
CITIES_SAMPLE = 2


@stub.function(
    secrets=[
        modal.Secret.from_name("TINYBIRD_KEY"),
        modal.Secret.from_name("PLUGSHARE_BASIC_KEY"),
    ],
)
def process_chargers():
    # Define Variables
    TINYBIRD_KEY = os.environ["TINYBIRD_KEY"]
    PLUGSHARE_BASIC_KEY = os.environ["PLUGSHARE_BASIC_KEY"]

    # Define functions
    def get_tb_data(url):
        cities_response = requests.get(url, params={"token": TINYBIRD_KEY})
        return pd.DataFrame(cities_response.json().get("data"))

    def get_ps_chargers(city):
        try:
            time.sleep(PS_SLEEP)
            print("City ", city["latitude"], ",", city["longitude"])
            url = "https://api.plugshare.com/v3/locations/region"
            params = {
                "access": 1,
                "count": 500,
                "exclude_poi_names": "dealership",
                "latitude": city["latitude"],
                "longitude": city["longitude"],
                "minimal": 0,
                "minimum_power": 149,
                "networks": "1,47,19,8",
                "outlets": '[{"connector":6,"power":1},{"connector":13,"power":0},{"connector":6,"power":0}]',
                "spanLat": 2.5,
                "spanLng": 2.5,
            }

            # Headers for the GET request
            headers = {
                "Accept": "application/json, text/plain, */*",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "en",
                "Authorization": f"Basic {PLUGSHARE_BASIC_KEY}",
                "Dnt": "1",
                "Origin": "https://www.plugshare.com",
                "Referer": "https://www.plugshare.com/",
                "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120"',
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": '"macOS"',
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-site",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            }

            response = requests.get(url, params=params, headers=headers)
            return response.json()
        except Exception as e:
            print(f"Error occurred: {e}")
        return None

    def process_charger(charger):
        network_id = (
            charger["stations"][0]["network_id"] if charger.get("stations") else None
        )
        kilowatts = [
            outlet["kilowatts"]
            for station in charger["stations"]
            for outlet in station["outlets"]
        ]

        return {
            "charger_id": charger["id"],
            "address": charger.get("address", "No address provided"),
            "network_id": network_id,
            "network_name": NETWORK_NAMES.get(network_id, "Unknown"),
            "min_kw": min(kilowatts) if kilowatts else None,
            "max_kw": max(kilowatts) if kilowatts else None,
            "count_stations": len(charger["stations"]),
            "lat": charger.get("latitude"),
            "long": charger.get("longitude"),
        }

    def insert_chargers(chargers, table_name):
        # Add a new column for the current UTC time
        chargers["inserted_at"] = datetime.utcnow().isoformat()
        events_dict_list = chargers.to_dict("records")
        data = "\n".join([json.dumps(event) for event in events_dict_list])

        params = {
            "name": table_name,
            "token": TINYBIRD_KEY,
        }

        r = requests.post(
            "https://api.us-east.tinybird.co/v0/events", params=params, data=data
        )

        print(r.status_code)
        print(r.text)

    ### Run Logic
    def main():
        cities_df = get_tb_data(
            "https://api.us-east.tinybird.co/v0/pipes/plugshare_cities_select.json"
        ).sample(CITIES_SAMPLE)

        chargers_df = get_tb_data(
            "https://api.us-east.tinybird.co/v0/pipes/plugshare_distinct_chargers.json"
        )

        if chargers_df.size > NUM_CHARGERS:
            print(f"At charger sample limit, num chargers: {chargers_df.size}")
            return

        chargers = []
        for index, row in cities_df.iterrows():
            results = get_ps_chargers(row)
            if results is not None:
                chargers.extend(results)

        processed_chargers = [process_charger(charger) for charger in chargers]
        processed_chargers = pd.DataFrame(processed_chargers)
        if len(chargers_df) > 0:
            processed_chargers_filtered = processed_chargers[
                ~processed_chargers["charger_id"].isin(chargers_df["charger_id"])
            ]
        else:
            processed_chargers_filtered = processed_chargers

        if len(processed_chargers_filtered) > 0:
            print("Num chargers to add", len(processed_chargers_filtered))
        else:
            print("No chargers to add")
            return

        insert_chargers(processed_chargers_filtered, "plugshare_chargers")

    return main()
