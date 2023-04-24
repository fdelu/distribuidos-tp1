from common.config import ConfigBase


class Config(ConfigBase):
    SECTION = "parsers"

    def __init__(self):
        super().__init__()
