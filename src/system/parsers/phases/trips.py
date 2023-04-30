import logging

from common.messages import End
from common.messages.raw import RawBatch

from . import Phase
from .parse import parse_trip


class TripsPhase(Phase):
    def handle_station_batch(self, batch: RawBatch) -> Phase:
        logging.warn("Unexpected Station received while receiving trips")
        return self

    def handle_weather_batch(self, batch: RawBatch) -> Phase:
        logging.warn("Unexpected Weather received while receiving trips")
        return self

    def handle_trip_batch(self, batch: RawBatch) -> Phase:
        self._send_parsed(batch, parse_trip)
        return self

    def handle_end(self) -> Phase:
        logging.info("Received End, waiting for all batchs to be processed")
        self.comms.set_all_batchs_done_callback(self._all_batchs_done)
        return self

    def _all_batchs_done(self):
        logging.info("Finished parsing all trips. Stopping...")
        self.comms.send(End())
        self.comms.stop_consuming()
