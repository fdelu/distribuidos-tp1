import logging
import os
import signal
from typing import Iterable

from shared.log import setup_logs

from .config import Config
from .bike_rides_analyzer import BikeRidesAnalyzer


def main():
    config = Config()
    setup_logs(config.log_level)

    bike_rides_analyzer = BikeRidesAnalyzer(config)
    bike_rides_analyzer.interrupt_on_signal(signal.SIGTERM)
    try:
        get_stats(bike_rides_analyzer, config)
    except (InterruptedError, KeyboardInterrupt):
        logging.info("Interrupted by user")

    bike_rides_analyzer.close()
    logging.info("Exiting gracefully")


def get_stats(bike_rides_analyzer: BikeRidesAnalyzer, config: Config):
    cities = os.listdir(config.data_path)
    logging.info(f"Using data in {config.data_path}. Cities: {', '.join(cities)}")

    for city in cities:
        path = f"{config.data_path}/{city}"
        bike_rides_analyzer.send_stations(city, line_reader(f"{path}/stations.csv"))
        bike_rides_analyzer.send_weather(city, line_reader(f"{path}/weather.csv"))

    for city in cities:
        path = f"{config.data_path}/{city}"
        bike_rides_analyzer.send_trips(city, line_reader(f"{path}/trips.csv"))

    rain_stats = bike_rides_analyzer.get_rain_averages()
    logging.info(f"Rain stats:\n{rain_stats}")


def line_reader(file_path: str) -> Iterable[str]:
    with open(file_path) as file:
        for line in file:
            yield line.strip()


main()
