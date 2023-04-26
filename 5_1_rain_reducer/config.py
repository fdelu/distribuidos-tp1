from common.config import ConfigBase


class Config(ConfigBase):
    SECTION = "rain_reducer"
    aggregators_count: int

    def __init__(self):
        super().__init__()
        self.aggregators_count = self.get_int("RainAggregatorsCount")
