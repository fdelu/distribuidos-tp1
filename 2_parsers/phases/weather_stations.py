import logging


from common.messages.basic import TripsStart
from common.messages.raw import RawBatch

from phases import Phase
from phases.trips import TripsPhase
from parse import parse_weather, parse_station


class WeatherStationsPhase(Phase):
    def handle_station_batch(self, batch: RawBatch) -> Phase:
        self._send_parsed(batch, parse_station)
        return self

    def handle_weather_batch(self, batch: RawBatch) -> Phase:
        self._send_parsed(batch, parse_weather)
        return self

    def handle_trip_batch(self, batch: RawBatch) -> Phase:
        self.comms.send(TripsStart())
        return TripsPhase(self.comms).handle_trip_batch(batch)

    def handle_end(self) -> Phase:
        logging.warn("Unexpected End received before getting any trips")
        return self
