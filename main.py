import modal
import os
from dotenv import dotenv_values

# Assuming modal.Image and modal.Stub work as expected with env vars
image = modal.Image.debian_slim().pip_install("python-dotenv")
stub = modal.Stub("plugshare-sentiment", image=image)
stub.envs = modal.Dict.new()


@stub.function()
def process_chargers():
    print("Starting to Process Chargers")
    # Function implementation
    return None


@stub.function()
def process_reviews():
    print("Starting to Process Reviews")
    # Function implementation
    return None


@stub.function(schedule=modal.Period(days=7))
def plugshare_sentiment():
    process_chargers.remote()
    process_reviews.remote()
    return None


@stub.local_entrypoint()
def main():
    plugshare_sentiment.remote()
    print("done")
