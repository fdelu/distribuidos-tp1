import logging

from common.messages.basic import BasicStation, BasicTrip, BasicWeather
from common.messages.joined import StationInfo

from . import Phase
from .trips import TripsPhase, WeatherData, StationData


class WeatherStationsPhase(Phase):
    parsers_sending_trips: int = 0
    ends_received: int = 0
    weather: WeatherData = {}
    stations: StationData = {}

    def handle_station(self, station: BasicStation) -> Phase:
        info = StationInfo(station.name, station.latitude, station.longitude)
        stations = self.stations.setdefault(station.city, {})
        stations[(station.code, station.year)] = info
        return self

    def handle_weather(self, weather: BasicWeather) -> "Phase":
        weathers = self.weather.setdefault(weather.city, {})
        weathers[weather.date] = weather.precipitation
        return self

    def handle_trips_start(self) -> Phase:
        self.parsers_sending_trips += 1
        logging.info(
            "A parser finished sending weather & stations"
            f" ({self.parsers_sending_trips}/{self.config.parsers_count})"
        )
        if self.parsers_sending_trips < self.config.parsers_count:
            return self

        logging.info("Receiving trips")
        self.comms.start_consuming_trips()
        trips_phase: Phase = TripsPhase(
            self.comms, self.config, self.weather, self.stations
        )
        for _ in range(self.ends_received):
            trips_phase = trips_phase.handle_end()
        return trips_phase

    def handle_trip(self, trip: BasicTrip) -> Phase:
        logging.warn("Unexpected Trip received while receiving weather & stations")
        return self

    def handle_end(self) -> Phase:
        self.ends_received += 1
        return self
