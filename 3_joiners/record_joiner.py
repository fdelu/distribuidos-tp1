import logging

from common.messages import End
from common.messages.basic import BasicRecord, BasicStation, BasicTrip, BasicWeather
from common.messages.joined import JoinedTrip, StationInfo

from comms import SystemCommunication
from config import Config


class RecordJoiner:
    receiving_trips: bool
    comms: SystemCommunication
    config: Config
    ends_received: int

    # city -> day -> precipitation
    weather: dict[str, dict[str, float]]

    # city -> (station code, year) -> station info
    stations: dict[str, dict[tuple[str, str], StationInfo]]

    def __init__(self, comms: SystemCommunication, config: Config):
        self.comms = comms
        self.config = config

        self.receiving_trips = False
        self.ends_received = 0

        self.weather = {}
        self.stations = {}

        logging.info("Receiving weather & stations")

    def handle_weather(self, weather: BasicWeather):
        if self.receiving_trips:
            logging.error("Received weather record after processing trips")
            return

        weathers = self.weather.setdefault(weather.city, {})
        weathers[weather.date] = weather.precipitation

    def handle_station(self, station: BasicStation):
        if self.receiving_trips:
            logging.error("Received station record after processing trips")
            return

        info = StationInfo(station.name, station.latitude, station.longitude)
        stations = self.stations.setdefault(station.city, {})
        stations[(station.code, station.year)] = info

    def get_station(self, city: str, code: str, year: str) -> StationInfo | None:
        station_info = self.stations[city].get((code, year), None)
        if station_info is None:
            logging.warn(f"Missing station info for code {code}, year {year} ({city})")
            logging.critical(self.stations)
        return station_info

    def get_join_data(
        self, trip: BasicTrip
    ) -> tuple[StationInfo, StationInfo, float] | None:
        start = self.get_station(trip.city, trip.start_station_code, trip.year)
        if start is None:
            return None

        end = self.get_station(trip.city, trip.end_station_code, trip.year)
        if end is None:
            return None

        weather = self.weather[trip.city].get(trip.start_date, None)
        if weather is None:
            logging.warn(f"Missing weather for date {trip.start_date} ({trip.city})")
            return None
        return start, end, weather

    def handle_trip(self, trip: BasicTrip):
        data = self.get_join_data(trip)
        if data is None:
            return

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
        self.comms.send_record(joined_trip)

    def handle_end(self):
        if self.receiving_trips:
            raise NotImplementedError("shutdown")
        self.ends_received += 1
        if self.ends_received >= self.config.parsers_count:
            logging.info("Receiving trips")
            self.receiving_trips = True
            self.comms.consume_trips()
        else:
            logging.info(
                "A parser finished sending stations and weather, waiting for others"
                f" ({self.ends_received}/{self.config.parsers_count})"
            )

    def handle_record(self, record: BasicRecord):
        if isinstance(record, End):
            self.handle_end()
        elif isinstance(record, BasicWeather):
            self.handle_weather(record)
        elif isinstance(record, BasicStation):
            self.handle_station(record)
        elif isinstance(record, BasicTrip):
            self.handle_trip(record)
        else:
            raise ValueError(f"Unknown record type: {record.record_type}")
