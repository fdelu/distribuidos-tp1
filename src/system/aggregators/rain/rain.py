from common.messages.joined import JoinedTrip
from common.messages.rain import DateInfo, PartialRainAverages


class RainAggregator:
    averages: dict[str, DateInfo]

    def __init__(self):
        self.averages = {}

    def handle_trip(self, trip: JoinedTrip):
        date_average = self.averages.setdefault(trip.start_date, DateInfo(0, 0))
        date_average.count += 1
        delta = (trip.duration_sec - date_average.average_duration) / date_average.count
        date_average.average_duration += delta

    def get_value(self) -> PartialRainAverages:
        return PartialRainAverages(self.averages)

    def reset(self):
        self.averages = {}
