#!/usr/bin/python3
import logging
import os

from shared.log import setup_logs

from .config import Config
from .bike_rides_analyzer import BikeRidesAnalyzer


def main():
    config = Config()
    setup_logs(config.log_level)
    bike_rides_analyzer = BikeRidesAnalyzer(config)
    cities = os.listdir(config.data_path)
    logging.info(f"Using data in {config.data_path}. Cities: {', '.join(cities)}")

    for city in cities:
        path = f"{config.data_path}/{city}"
        bike_rides_analyzer.send_stations(city, f"{path}/stations.csv")
        bike_rides_analyzer.send_weather(city, f"{path}/weather.csv")

    for city in cities:
        path = f"{config.data_path}/{city}"
        bike_rides_analyzer.send_trips(city, f"{path}/trips.csv")

    bike_rides_analyzer.process_results()
    rain_stats = bike_rides_analyzer.get_rain_averages()
    logging.info(f"Rain stats:\n{rain_stats}")


main()
