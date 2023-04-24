import zmq

from common.log import setup_logs
from handler import ClientHandler

from config import Config


def main():
    config = Config()
    setup_logs(config.log_level)

    context = zmq.Context()
    socket = context.socket(zmq.PAIR)
    socket.bind(f"tcp://*:{config.port}")

    handler = ClientHandler(config, socket)
    handler.get_records()


main()
