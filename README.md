# Plugshare Sentiment Analysis of Checkin Comments

## Introduction
This repo contains the code used in scraping, processing, and storing data from Plugshare Checkin Comments in order to do sentiment analysis of those comments. The goal is to track and analyze the current state of charging by the top electric vehicle DC fast chargers in the US. Sentiment analysis is accomplished through OpenAI's GPT 3 model to rate each comment in one of three categories

## Repo
This repo has the following files and structure
- **pkg**: The main code for running these functions. It is broken down into the following files.
    - **tasks.py**: Modal function which orchestrates the two other functions.
    - **chargers.py**: Modal function which samples chargers and saves them to Tinybird.
    - **reviews.py**: Modal function which takes charger checkin comments, and processes them with sentiment analysis.
    - **common.py**: Shared config for Modal functions.
- **cities.json**: Data from this [repo](https://gist.github.com/Miserlou/c5cd8364bf9b2420bb29#file-cities-json)
- **test.ipynb**: Scratch file for testing (it's a little messy lol)

## Installation
If anyone wants to install this to conduct their own analysis the main requirements are found in requirements.txt. I also utilized [Modal](https://modal.com/) and [Tinybird](https://www.tinybird.co/) and any code using those two platforms would require you to set those up too. 

*Please use responsibly*