import logging

from shared.log import setup_logs

from .reducer import AverageReducer
from .config import Config

trips = False


def main():
    config = Config()
    setup_logs(config.log_level)

    counter = AverageReducer(config)
    counter.run()
    logging.info("Exiting gracefully")


main()
