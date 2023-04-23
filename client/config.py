import configparser


class Config:
    batch_size: int
    input_address: str

    SECTION = "client"

    def __init__(self):
        parser = configparser.ConfigParser()
        parser.read("/config.ini")
        self.batch_size = parser.getint(self.SECTION, "BatchSize")
        self.input_address = parser.get(self.SECTION, "InputAddress")
