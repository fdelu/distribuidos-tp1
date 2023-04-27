from common.messages.basic import BasicRecord, BasicStation, BasicTrip, BasicWeather

from config import Config
from comms import SystemCommunication


class Phase:
    comms: SystemCommunication
    config: Config

    def __init__(self, comms: SystemCommunication, config: Config):
        self.comms = comms
        self.config = config

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
