from common.config import ConfigBase


class Config(ConfigBase):
    address: str

    SECTION = "input"

    def __init__(self):
        super().__init__()
        self.address = self.get("Address")
