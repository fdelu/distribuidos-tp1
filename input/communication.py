from pika import BasicProperties, BlockingConnection, ConnectionParameters
from config import Config


class SystemCommunication:
    def __init__(self, config: Config):
        self.connection = BlockingConnection(
            ConnectionParameters(host=config.rabbit_host)
        )
        self.channel = self.connection.channel()
        self.setup_queues()

        self.pending_responses = 0

    def setup_queues(self):
        self.channel.queue_declare(queue="raw_records")
        self.channel.queue_declare(queue="raw_records_callback")
        self.channel.basic_consume(
            queue="raw_records_callback", on_message_callback=self.handle_response
        )

    def handle_response(self, ch, method, props, body):
        self.pending_responses -= 1

    def send_record(self, record: str):
        props = BasicProperties(reply_to="raw_records_callback")
        self.channel.basic_publish(
            exchange="", routing_key="raw_records", body=record, properties=props
        )
        self.pending_responses += 1

    def wait_for_weather_stations(self):
        while self.pending_responses > 0:
            self.connection.process_data_events(time_limit=None)
