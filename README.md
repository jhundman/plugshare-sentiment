# Plugshare Sentiment Analysis of Checkin Comments

Check out this [dashboard](https://hayeshundman.io/projects/plugshare-sentiment) and this [blog post](https://hayeshundman.io/blog/state-of-charging) the repo powers!

## Introduction
This repo contains the code used in scraping, processing, and storing data from Plugshare Checkin Comments in order to do sentiment analysis of those comments. The goal is to track and analyze the current state of charging by the top electric vehicle DC fast chargers in the US. Sentiment analysis is accomplished through OpenAI's GPT 3 model to rate each comment in one of three categories.

## Process
In order to get chargers I would randomly sample latitudes and longitudes of the top 1000 US cities. From there I would jitter the locations a bit to get any new chargers. I also only looked for chargers from Tesla, Electrify America, EVgo, and Chargepoint over 149kw speed. Sadly Plugshare does not yet break out Rivian's RAN network chargers :(. From there I would sample chargers and grab all the check-ins. Plugshare only surfaces the most recent 50 I believe and I filter out ones with data that is not useful. From there I used GPT 3.5 with the following prompt to accomplish sentiment analysis. 

```
 Rate the following variables of an EV charger based on a user comment using a 0-1 scale. Default to 0.75 (good) if information is insufficient. Provide a JSON response with three variables and corresponding float values.

                1. charging: Assess speed and reliability of charging hardware and software.
                    - 1: Fast, flawless.
                    - 0.75: Decent speed, no major issues, or unknown.
                    - 0.5: Minor issues.
                    - 0.25: Slow, problematic.
                    - 0: Inoperative.

                2. busy: Evaluate crowding.
                    - 1: Not busy.
                    - 0.75: Slightly busy, no delay, or unknown.
                    - 0.5: Busy with no wait.
                    - 0.25: Busy with wait.
                    - 0: Overcrowded, long wait.

                3. location: Judge area quality and amenities.
                    - 1: Excellent area, ample amenities.
                    - 0.75: Good area, some amenities, or unknown.
                    - 0.5: Average.
                    - 0.25: Below average.
                    - 0: Poor, no amenities.

                Rate the following user-reported EV charger details:
                - Comment:
                - Had Charging Problem(optional default 0): 
                - Problem Description:
```

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
If anyone wants to install this to conduct their own analysis the main requirements are found in requirements.txt. I also utilized [Modal](https://modal.com/), [Tinybird](https://www.tinybird.co/), and OpenAI's API. 
