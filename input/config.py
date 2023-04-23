import configparser


class Config:
    port: int
    rabbit_host: str
    log_level: str | None

    SECTION = "input"

    def __init__(self):
        parser = configparser.ConfigParser()
        parser.read("/config.ini")
        self.port = parser.getint(self.SECTION, "Port")
        self.log_level = parser.get(self.SECTION, "LogLevel", fallback=None)
        self.rabbit_host = parser.get(configparser.DEFAULTSECT, "RabbitHost")
