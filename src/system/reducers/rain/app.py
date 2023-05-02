import logging
from shared.log import setup_logs

from ..common.reducer import ReductionHandler
from common.messages.aggregated import PartialRainAverages
from common.messages.stats import RainAverages
from .rain import RainReducer
from ..common.config import Config

from .comms import SystemCommunication

NAME = "rain"


def main():
    config = Config(NAME)
    setup_logs(config.log_level)

    comms = SystemCommunication(config)
    reducer = RainReducer()
    handler = ReductionHandler[PartialRainAverages, RainAverages](
        config, reducer, comms
    )
    handler.run()
    logging.info("Exiting gracefully")


main()
