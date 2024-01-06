# import pandas as pd
# import requests
# from dotenv import load_dotenv
# import os
# import json
import modal

stub = modal.Stub("example-get-started")


@stub.function()
def square(x):
    print("This code is running on a remote worker!")
    return x**2


@stub.local_entrypoint()
def main():
    print("the square is", square.remote(42))
