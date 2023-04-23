import configparser


class Config:
    rabbit_host: str

    SECTION = "parser"

    def __init__(self):
        parser = configparser.ConfigParser()
        parser.read("/config.ini")
        self.rabbit_host = parser.get("rabbitmq", "Host")
