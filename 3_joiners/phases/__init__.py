from common.messages.basic import BasicRecord, BasicStation, BasicTrip, BasicWeather
from common.messages.joined import StationInfo

from config import Config
from comms import SystemCommunication


class Phase:
    comms: SystemCommunication
    config: Config

    # city -> day -> precipitation
    weather: dict[str, dict[str, float]]

    # city -> (station code, year) -> station info
    stations: dict[str, dict[tuple[str, str], StationInfo]]

    def __init__(self, comms: SystemCommunication, config: Config):
        self.comms = comms
        self.config = config

        self.weather = {}
        self.stations = {}

    def handle_weather(self, weather: BasicWeather) -> "Phase":
        raise NotImplementedError()

    def handle_station(self, station: BasicStation) -> "Phase":
        raise NotImplementedError()

    def handle_trips_start(self) -> "Phase":
        raise NotImplementedError()

    def handle_trip(self, trip: BasicTrip) -> "Phase":
        raise NotImplementedError()

    def handle_end(self) -> "Phase":
        raise NotImplementedError()

    def handle_record(self, record: BasicRecord) -> "Phase":
        return record.be_handled_by(self)
