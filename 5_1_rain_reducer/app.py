from reducer import AverageReducer
from common.log import setup_logs
from comms import SystemCommunication

from config import Config

trips = False


def main():
    config = Config()
    setup_logs(config.log_level)

    comms = SystemCommunication(config)
    comms.setup()
    counter = AverageReducer(comms)
    comms.start_consuming(counter.handle_record)


main()
