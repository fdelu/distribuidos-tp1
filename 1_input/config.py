from common.config import ConfigBase


class Config(ConfigBase):
    port: int

    SECTION = "input"

    def __init__(self):
        super().__init__()
        self.port = self.get_int("Port")
