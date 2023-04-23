import zmq

from common.log import setup_logs
from input.handler import ClientHandler

from config import Config

setup_logs()


def main():
    config = Config()

    context = zmq.Context()
    socket = context.socket(zmq.PAIR)
    socket.bind(f"tcp://*:{config.port}")

    handler = ClientHandler(config, socket)
    handler.get_records()


main()
