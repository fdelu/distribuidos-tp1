import logging
from typing import Any, Generic, Protocol, TypeVar

from common.messages import End
from common.messages.joined import GenericJoinedRecord
from common.comms_base import SystemCommunicationBase

from .config import Config

T = TypeVar("T", covariant=True, bound=End)


class Aggregator(Protocol[GenericJoinedRecord, T]):
    def handle_joined(self, trip: GenericJoinedRecord):
        ...

    def get_value(self) -> T:
        ...

    def reset(self):
        ...


class AggregationHandler(Generic[T, GenericJoinedRecord]):
    comms: SystemCommunicationBase[GenericJoinedRecord | End, T]
    aggregator: Aggregator[GenericJoinedRecord, T]
    config: Config
    timer: Any | None
    ends_received: int

    def __init__(
        self,
        comms: SystemCommunicationBase[GenericJoinedRecord | End, T],
        aggregator: Aggregator,
        config: Config,
    ):
        self.config = config
        self.comms = comms
        self.aggregator = aggregator
        self.ends_received = 0
        self.timer = None

    def run(self):
        self.comms.set_callback(self.handle_record)
        self.comms.start_consuming()
        self.comms.close()

    def handle_joined(self, trip: GenericJoinedRecord):
        self.aggregator.handle_joined(trip)

        if self.timer is None:
            self.setup_timer()

    def handle_end(self):
        self.ends_received += 1
        logging.debug(
            "A joiner finished sending trips"
            f" ({self.ends_received}/{self.config.joiners_count})"
        )
        if self.ends_received < self.config.joiners_count:
            return
        logging.info("Waiting for all trips to be processed")
        self.comms.set_all_trips_done_callback(self.finished)

    def handle_record(self, record: GenericJoinedRecord):
        record.be_handled_by(self)

    def finished(self):
        logging.info("All trips processed, sending final partial averages")
        if self.timer is not None:
            self.comms.cancel_timer(self.timer)
            self.timer = None

        self.send_averages()
        self.comms.send(End())
        self.comms.stop_consuming()

    def timer_callback(self):
        self.send_averages()
        self.setup_timer()

    def setup_timer(self):
        self.timer = self.comms.set_timer(
            self.timer_callback, self.config.send_interval_seconds
        )

    def send_averages(self):
        logging.debug("Sending partial results")
        self.comms.send(self.aggregator.get_value())
        self.averages = {}
