from common.config_base import ConfigBase


class Config(ConfigBase):
    address: str

    def __init__(self):
        super().__init__("output")
        self.address = self.get("Address")
