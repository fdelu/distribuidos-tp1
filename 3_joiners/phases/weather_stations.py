import logging

from common.messages.basic import BasicStation, BasicTrip, BasicWeather
from common.messages.joined import StationInfo

from phases import Phase
from phases.trips import TripsPhase


class WeatherStationsPhase(Phase):
    parsers_done: int = 0

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
        self.parsers_done += 1
        if self.parsers_done < self.config.parsers_count:
            logging.info(
                "A parser finished sending stations and weather, waiting for others"
                f" ({self.parsers_done}/{self.config.parsers_count})"
            )
            return self

        logging.info("Receiving trips")
        self.comms.start_consuming_trips()
        return TripsPhase(self.comms, self.config)

    def handle_trip(self, trip: BasicTrip) -> Phase:
        logging.warn("Unexpected Trip received while receiving weather & stations")
        return self

    def handle_end(self) -> Phase:
        logging.warn("Unexpected End received before getting any trips")
        return self
