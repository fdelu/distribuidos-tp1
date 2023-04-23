#!/usr/bin/python3
import os
from bike_rides_analyzer import BikeRidesAnalyzer

DATA_PATH = "/tmp/data"


def main():
    bike_rides_analyzer = BikeRidesAnalyzer()
    cities = os.listdir(DATA_PATH)

    for city in cities:
        bike_rides_analyzer.send_stations(city, f"{DATA_PATH}/{city}/stations.csv")
        bike_rides_analyzer.send_weather(city, f"{DATA_PATH}/{city}/weather.csv")

    for city in cities:
        bike_rides_analyzer.send_trips(city, f"{DATA_PATH}/{city}/trips.csv")

    bike_rides_analyzer.get_results()


main()
