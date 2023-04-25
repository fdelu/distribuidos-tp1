import zmq
from threading import Thread

from common.log import setup_logs

from stats_receiver import StatsReceiver
from handler import ClientHandler
from config import Config


def main():
    config = Config()
    setup_logs(config.log_level)
    context = zmq.Context()

    stat_receiver = StatsReceiver(config)
    client_handler = ClientHandler(config, context, stat_receiver)

    thread = Thread(target=client_handler.run)
    thread.start()
    stat_receiver.run()


main()
