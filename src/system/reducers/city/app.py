import logging
from shared.log import setup_logs

from ..common.reducer import ReductionHandler
from common.messages.aggregated import PartialRainRecords
from .city import CityReducer

from .config import Config
from .comms import SystemCommunication


def main():
    config = Config()
    setup_logs(config.log_level)

    comms = SystemCommunication(config)
    reducer = CityReducer(config)
    handler = ReductionHandler[PartialRainRecords](config, reducer, comms)
    handler.run()
    logging.info("Exiting gracefully")


main()
