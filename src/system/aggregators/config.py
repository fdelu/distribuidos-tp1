from common.config import ConfigBase


class Config(ConfigBase):
    SECTION = "rain_aggregator"

    joiners_count: int
    send_interval_seconds: float

    def __init__(self):
        super().__init__()
        self.send_interval_seconds = self.get_float("SendIntervalSeconds")
        self.joiners_count = self.get_int("JoinersCount")
