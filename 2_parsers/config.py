import configparser


class Config:
    rabbit_host: str
    log_level: str | None

    SECTION = "parser"

    def __init__(self):
        parser = configparser.ConfigParser()
        parser.read("/config.ini")
        self.log_level = parser.get(self.SECTION, "LogLevel", fallback=None)
        self.rabbit_host = parser.get(configparser.DEFAULTSECT, "RabbitHost")
