from common.config import ConfigBase


class Config(ConfigBase):
    address: str

    SECTION = "output"

    def __init__(self):
        super().__init__()
        self.address = self.get("Address")
