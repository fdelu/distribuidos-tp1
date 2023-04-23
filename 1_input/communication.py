from pika import BlockingConnection, ConnectionParameters
from config import Config


class SystemCommunication:
    def __init__(self, config: Config):
        self.connection = BlockingConnection(
            ConnectionParameters(host=config.rabbit_host)
        )
        self.channel = self.connection.channel()
        self.setup_queues()

    def setup_queues(self):
        # out
        self.channel.queue_declare(queue="raw_records")

    def send_record(self, record: str):
        self.channel.basic_publish(exchange="", routing_key="raw_records", body=record)
