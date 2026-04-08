# -cis4930-sp26-project-group-2
Build a small but real automation pipeline that calls a public API, collects data, and store data locally. 

## Real World Context
It gathers real-time weather forecasts for three different cities to see how weather compares in different parts of the United States. This can be used to see if different weather patterns are unique to the area or will migrate to another.

## Data Pipeline Goals:
- Fetch current temperature as well as daily and hourly weather information such as precipitaion probability and temperature max and min.
- Fetch weather forecasts for multiple cities.
- Store weather forecasts in a database and CSV file.
- Automate the processs to gather a seven day forecast each run.
- Log operations and errors efficiently.

## Link to API
https://open-meteo.com/

## Run Script
### Install 
pip install requests-cache retry-requests numpy pandas  
pip install requests
### Run
python -m pipeline

## Members
- Jeremiah Daniels - jbd22a
- Zachary Bryan - zbb21
- Kobus Vansteenburg - kmv21a
- Ammiel Bowen - ab22dv


