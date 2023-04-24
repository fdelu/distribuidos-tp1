from common.log import setup_logs
from comms import SystemCommunication

from config import Config
from record_joiner import RecordJoiner

trips = False


def main():
    config = Config()
    setup_logs(config.log_level)

    comms = SystemCommunication(config)
    comms.setup()
    joiner = RecordJoiner(comms, config)
    comms.start_consuming(joiner.handle_record)


main()
