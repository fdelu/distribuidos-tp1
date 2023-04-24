from common.config import ConfigBase


class Config(ConfigBase):
    parsers_count: int
    precipitation_threshold: float

    SECTION = "joiners"

    def __init__(self):
        super().__init__()
        self.parsers_count = self.get_int("ParsersCount")
        self.precipitation_threshold = self.get_float("PrecipitationThreshold")
