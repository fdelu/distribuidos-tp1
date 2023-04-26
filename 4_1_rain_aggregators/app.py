from aggregator import RainedAggregator
from common.log import setup_logs

from config import Config


def main():
    config = Config()
    setup_logs(config.log_level)

    counter = RainedAggregator(config)
    counter.run()


main()
