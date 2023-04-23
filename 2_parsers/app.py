import logging
from common.log import setup_logs
from communication import SystemCommunication

from config import Config
from parsers.parser import RecordParser

trips = False


def main():
    config = Config()
    setup_logs(config.log_level)
    parser = RecordParser()

    logging.info("Receiving weather & stations")
    comms = SystemCommunication(config, parser.handle_record)
    comms.start_consuming()


main()
