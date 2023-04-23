import configparser
import os


class Config:
    rabbit_host: str
    parsers_count: int
    log_level: str | None

    SECTION = "parser"

    def __init__(self):
        parser = configparser.ConfigParser()
        parser.read("/config.ini")
        self.log_level = parser.get(self.SECTION, "LogLevel", fallback=None)
        self.parsers_count = parser.getint(
            configparser.DEFAULTSECT, "ParsersCount", vars=os.environ
        )
        self.rabbit_host = parser.get(configparser.DEFAULTSECT, "RabbitHost")
