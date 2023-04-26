import logging

from common.messages import End
from common.messages.basic import BasicStation, BasicTrip, BasicWeather
from common.messages.joined import JoinedTrip, StationInfo

from phases import Phase


class TripsPhase(Phase):
    ends_received: int = 0

    def handle_station(self, station: BasicStation) -> Phase:
        logging.warn("Unexpected Station received while receiving trips")
        return self

    def handle_weather(self, weather: BasicWeather) -> Phase:
        logging.warn("Unexpected Weather received while receiving trips")
        return self

    def handle_trips_start(self) -> Phase:
        logging.warn("Unexpected TripsStart received while already receiving trips")
        return self

    def handle_trip(self, trip: BasicTrip) -> Phase:
        data = self._get_join_data(trip)
        if data is None:
            return self

        start, end, precipitation = data
        joined_trip = JoinedTrip(
            trip.start_date,
            start,
            end,
            precipitation > self.config.precipitation_threshold,
            trip.duration_sec,
            trip.year,
            trip.city,
        )
        self.comms.send(joined_trip)
        return self

    def handle_end(self) -> Phase:
        self.ends_received += 1
        if self.ends_received < self.config.parsers_count:
            logging.info(
                "A parser finished sending trips, waiting for others"
                f" ({self.ends_received}/{self.config.parsers_count})"
            )
            return self
        logging.info("All parsers finished sending trips, waiting until all are joined")
        self.comms.set_all_trips_done_callback(self._all_trips_done)
        return self

    def _get_join_data(
        self, trip: BasicTrip
    ) -> tuple[StationInfo, StationInfo, float] | None:
        start = self._get_station(trip.city, trip.start_station_code, trip.year)
        if start is None:
            return None

        end = self._get_station(trip.city, trip.end_station_code, trip.year)
        if end is None:
            return None

        weather = self.weather[trip.city].get(trip.start_date, None)
        if weather is None:
            logging.warn(f"Missing weather for date {trip.start_date} ({trip.city})")
            return None
        return start, end, weather

    def _get_station(self, city: str, code: str, year: str) -> StationInfo | None:
        station_info = self.stations[city].get((code, year), None)
        if station_info is None:
            logging.warn(f"Missing station info for code {code}, year {year} ({city})")
            logging.critical(self.stations)
        return station_info

    def _all_trips_done(self):
        logging.info("Finished joining all trips. Stopping...")
        self.comms.send(End())
        self.comms.stop_consuming()
