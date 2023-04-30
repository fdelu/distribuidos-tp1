from common.config_base import ConfigBase


class Config(ConfigBase):
    aggregators_count: int

    def __init__(self):
        super().__init__("reducers.rain")
        self.aggregators_count = self.get_int("RainAggregatorsCount")
