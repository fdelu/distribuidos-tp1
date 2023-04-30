from common.config_base import ConfigBase


class Config(ConfigBase):
    parsers_count: int
    precipitation_threshold: float

    def __init__(self):
        super().__init__("joiners")
        self.parsers_count = self.get_int("ParsersCount")
        self.precipitation_threshold = self.get_float("PrecipitationThreshold")
