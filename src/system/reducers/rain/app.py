import logging
from shared.log import setup_logs

from ..common.reducer import ReductionHandler
from common.messages.rain import PartialRainRecords
from .rain import RainReducer
from ..common.config import Config

from .comms import SystemCommunication

NAME = "rain"


def main():
    config = Config(NAME)
    setup_logs(config.log_level)

    comms = SystemCommunication(config)
    reducer = RainReducer()
    handler = ReductionHandler[PartialRainRecords](config, reducer, comms)
    handler.run()
    logging.info("Exiting gracefully")


main()
