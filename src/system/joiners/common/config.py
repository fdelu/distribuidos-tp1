from common.config_base import ConfigBase


class Config(ConfigBase):
    parsers_count: int

    def __init__(self, name: str):
        super().__init__(f"joiners.{name}")
        self.parsers_count = self.get_int("ParsersCount")
