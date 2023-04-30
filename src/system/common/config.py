import os
from configparser import ConfigParser, DEFAULTSECT
from typing import ClassVar

CONFIG_PATH = "/config.ini"


class ConfigBase:
    parser: ConfigParser
    rabbit_host: str
    log_level: str | None
    prefetch_count: int

    SECTION: ClassVar[str] = DEFAULTSECT

    def __init__(self):
        self.parser = ConfigParser()
        self.parser.read(CONFIG_PATH)
        self.log_level = self.get("LogLevel", fallback=None)
        self.rabbit_host = self.get("RabbitHost")
        self.prefetch_count = self.get_int("PrefetchCount")

    def get(self, key: str, **kwargs) -> str:
        return self.parser.get(self.SECTION, key, vars=os.environ, **kwargs)

    def get_int(self, key: str, **kwargs) -> int:
        return self.parser.getint(self.SECTION, key, vars=os.environ, **kwargs)

    def get_float(self, key: str, **kwargs) -> float:
        return self.parser.getfloat(self.SECTION, key, vars=os.environ, **kwargs)

    def get_bool(self, key: str, **kwargs) -> bool:
        return self.parser.getboolean(self.SECTION, key, vars=os.environ, **kwargs)
