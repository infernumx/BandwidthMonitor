from datetime import datetime
from dataclasses import dataclass


@dataclass
class NetworkData:
    sent: float
    received: float
    time: datetime

    def __repr__(self):
        return "NetworkData({}, {}, {})".format(
            self.sent, self.received, repr(self.time)
        )

    def __str__(self):
        time_str = self.time.strftime("%Y-%m-%d %H:%M:%S")
        return "[{}]: Sent: {:.2f} MB | Received: {:.2f} MB".format(
            time_str, round(self.sent, 2), round(self.received, 2)
        )

    def __sub__(self, b):
        return NetworkData(
            self.sent - b.sent, self.received - b.received, datetime.now()
        )
