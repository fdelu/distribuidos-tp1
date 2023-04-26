import logging

from common.messages.basic import BasicRecord

from phases import Phase
from phases.weather_stations import WeatherStationsPhase
from comms import SystemCommunication
from config import Config


class RecordJoiner:
    comms: SystemCommunication
    config: Config

    phase: Phase

    def __init__(self, config: Config):
        self.comms = SystemCommunication(config)
        self.config = config
        self.phase = WeatherStationsPhase(self.comms, config)

    def run(self):
        logging.info("Receiving weather & stations")
        self.comms.set_callback(self.handle_record)
        self.comms.start_consuming()

    def handle_record(self, record: BasicRecord):
        self.phase = self.phase.handle_record(record)
