from pika import BlockingConnection, ConnectionParameters
from pika.adapters.blocking_connection import BlockingChannel

from common.config_base import ConfigBase

from .protocol import CommsProtocol

from .send import CommsSend  # noqa
from .receive import CommsReceive  # noqa


# Base communication class. See protocol.py for more details about the methods.
class SystemCommunicationBase(CommsProtocol):
    conn: BlockingConnection
    ch: BlockingChannel

    @property
    def connection(self) -> BlockingConnection:
        return self.conn

    @property
    def channel(self) -> BlockingChannel:
        return self.ch

    def __init__(self, config: ConfigBase):
        self.conn = BlockingConnection(ConnectionParameters(host=config.rabbit_host))
        self.ch = self.conn.channel()
        self.ch.basic_qos(prefetch_count=config.prefetch_count)

    def close(self):
        self.ch.close()
        self.conn.close()
