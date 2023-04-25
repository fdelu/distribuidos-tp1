from common.log import setup_logs

from config import Config
from record_joiner import RecordJoiner

trips = False


def main():
    config = Config()
    setup_logs(config.log_level)

    joiner = RecordJoiner(config)
    joiner.run()


main()
