#!/usr/bin/python3
import logging
import os
from bike_rides_analyzer import BikeRidesAnalyzer
from common.log import setup_logs


setup_logs()
DATA_PATH = "/tmp/data"


def main():
    bike_rides_analyzer = BikeRidesAnalyzer()
    cities = os.listdir(DATA_PATH)

    logging.info("Sending stations and weather")
    for city in cities:
        bike_rides_analyzer.send_stations(city, f"{DATA_PATH}/{city}/stations.csv")
        bike_rides_analyzer.send_weather(city, f"{DATA_PATH}/{city}/weather.csv")

    logging.info("Sending trips")
    for city in cities:
        bike_rides_analyzer.send_trips(city, f"{DATA_PATH}/{city}/trips.csv")

    logging.info("Waiting for results")
    bike_rides_analyzer.get_results()


main()
