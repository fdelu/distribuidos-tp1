import logging
from shared.log import setup_logs

from ..common.aggregator import AggregationHandler
from common.messages.rain import PartialRainRecords
from .rain import RainAggregator
from ..common.config import Config

from .comms import SystemCommunication

NAME = "rain"


def main():
    config = Config(NAME)
    setup_logs(config.log_level)

    comms = SystemCommunication(config)
    aggregator = RainAggregator()
    handler = AggregationHandler[PartialRainRecords](comms, aggregator, config)
    handler.run()
    logging.info("Exiting gracefully")


main()
