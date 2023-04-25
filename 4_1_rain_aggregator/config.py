from common.config import ConfigBase


class Config(ConfigBase):
    SECTION = "rain_aggregator"

    def __init__(self):
        super().__init__()
