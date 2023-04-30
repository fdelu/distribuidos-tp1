from common.config_base import ConfigBase


class Config(ConfigBase):
    joiners_count: int
    send_interval_seconds: float

    def __init__(self, name: str):
        super().__init__(f"aggregators.{name}")
        self.send_interval_seconds = self.get_float("SendIntervalSeconds")
        self.joiners_count = self.get_int("RainJoinersCount")
