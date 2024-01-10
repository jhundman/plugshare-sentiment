import modal
import os
import requests
import pandas as pd

base_image = modal.Image.debian_slim().pip_install("requests", "pandas")
stub = modal.Stub(
    "plugshare-sentiment",
    image=base_image,
)


@stub.function(
    secrets=[
        modal.Secret.from_name("TINYBIRD_KEY"),
        modal.Secret.from_name("PLUGSHARE_BASIC_KEY"),
    ],
)
def process_chargers():
    print("Charger Function")
    TINYBIRD_KEY = os.environ["TINYBIRD_KEY"]
    PLUGSHARE_BASIC_KEY = os.environ["TINYBIRD_KEY"]

    def get_tb_data(url):
        cities_response = requests.get(url, params={"token": TINYBIRD_KEY})
        return pd.DataFrame(cities_response.json().get("data"))

    cities_df = get_tb_data(
        "https://api.us-east.tinybird.co/v0/pipes/plugshare_cities_select.json"
    ).sample(5, random_state=1056)

    chargers_df = get_tb_data(
        "https://api.us-east.tinybird.co/v0/pipes/plugshare_distinct_chargers.json"
    )

    print("Cities Shape", cities_df.shape)
    print("Chargers Shape", chargers_df.shape)

    return None


@stub.function()
def process_reviews():
    print("Review Function")
    return None


@stub.function(schedule=modal.Period(days=7))
def plugshare_sentiment():
    print("Starting Script")
    print("==== Starting to Process Chargers =====")
    process_chargers.remote()
    print("==== Starting to Process Reviews =====")
    process_reviews.remote()
    return None


@stub.local_entrypoint()
def main():
    plugshare_sentiment.remote()
    print("Script Complete")
    return
