from common.config import ConfigBase


class Config(ConfigBase):
    SECTION = "rain_reducer"

    def __init__(self):
        super().__init__()
