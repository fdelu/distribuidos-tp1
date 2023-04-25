import logging
import zmq

from config import Config
from stats_receiver import StatType, StatsReceiver

END = "END"


class ClientHandler:
    config: Config
    stats: StatsReceiver

    context: zmq.Context
    socket: zmq.Socket
    control: zmq.Socket

    pending: dict[StatType, list[bytes]] = {}  # stat_type -> clients waiting

    def __init__(self, config: Config, context: zmq.Context, stats: StatsReceiver):
        self.stats = stats
        stats.add_listener(self)

        self.context = context
        self.socket = context.socket(zmq.ROUTER)
        self.socket.bind(config.address)

        self.control = context.socket(zmq.PAIR)
        self.control.bind("inproc://control")

    def run(self):
        logging.info("Client handler started")
        poller = zmq.Poller()
        poller.register(self.socket, zmq.POLLIN)
        poller.register(self.control, zmq.POLLIN)
        stop = False
        while not stop:
            stop = self.__receive(poller)
        self.socket.close()
        self.control.close()

    def stop(self):
        """
        Stops a runnin server
        Thread-safe method.
        """
        self.control.send_string(END)

    def received(self, type: StatType):
        """
        Queues the given stat to be sent to all clients waiting for it.
        Thread-safe method.
        """
        socket: zmq.Socket = self.context.socket(zmq.PAIR)
        socket.connect("inproc://control")
        socket.send_string(type)

    def __receive(self, poller: zmq.Poller) -> bool:
        """
        Receives a message. Returns True if the server should stop.
        """
        ready = [x[0] for x in poller.poll()]
        if self.control in ready:
            msg = self.control.recv_string()
            if msg == END:
                return True
            self.__handle_received(StatType(msg))

        if self.socket in ready:
            id, _, body = self.socket.recv_multipart()
            self.__handle_client(id, body)
        return False

    def __handle_received(self, type: StatType):
        """
        Sends a stat to all clients waiting for it when it is received
        """
        waiting = self.pending.pop(type, [])
        for id in waiting:
            stat = self.stats.get(type)
            if stat is None:
                raise RuntimeError("Stat was received but not available")
            self.__send_stat(id, stat)

    def __handle_client(self, id: bytes, msg: bytes):
        """
        Handles a client request, either by sending him the stat he
        requested or by adding him to the list of clients waiting for that stat
        """
        msg_str = msg.decode()
        logging.info(f"Received request for stats {msg_str}")
        try:
            type = StatType(msg_str)
        except ValueError:
            logging.warning(f"Invalid stat type was requested: {msg_str}")
            self.socket.send_multipart([id, b"", b"Invalid stat type"])
            return
        stat = self.stats.get(type)
        if stat is None:
            self.pending.setdefault(type, []).append(id)
        else:
            self.__send_stat(id, stat)

    def __send_stat(self, id: bytes, stat: str):
        """
        Sends a stat to a client
        """
        logging.info("Sending response to client")
        self.socket.send_multipart([id, b"", stat.encode()])
