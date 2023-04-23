import configparser


class Config:
    port: int
    rabbit_host: str

    SECTION = "input"

    def __init__(self):
        parser = configparser.ConfigParser()
        parser.read("/config.ini")
        self.port = parser.getint(self.SECTION, "Port")
        self.rabbit_host = parser.get("rabbitmq", "Host")
