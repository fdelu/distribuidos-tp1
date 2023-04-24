from common.log import setup_logs
from comms import SystemCommunication

from config import Config
from record_parser import RecordParser

trips = False


def main():
    config = Config()
    setup_logs(config.log_level)

    comms = SystemCommunication(config)
    comms.setup()
    parser = RecordParser(comms)
    comms.start_consuming(parser.handle_record)


main()
