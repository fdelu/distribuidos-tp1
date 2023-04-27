import logging
from reducer import AverageReducer
from common.log import setup_logs

from config import Config

trips = False


def main():
    config = Config()
    setup_logs(config.log_level)

    counter = AverageReducer(config)
    counter.run()
    logging.info("Exiting gracefully")


main()
