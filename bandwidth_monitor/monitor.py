from .network_data import NetworkData
from datetime import datetime
from typing import List
from threading import Thread
import psutil
import time
import platform
import os


class BandwidthMonitor:
    def __init__(self, on_update: callable, interval=60):
        self.on_update = on_update
        self.interval = interval
        self.total_runs: List[NetworkData] = []
        self.base: NetworkData = self.new_bandwidth_difference(init=True)

    def new_bandwidth_difference(self, init=False):
        """Retrieves the bandwidth difference from the base"""
        data = psutil.net_io_counters()
        network_data = NetworkData(
            data.bytes_sent / 1000000, data.bytes_recv / 1000000, datetime.now()
        )
        if not init:
            network_data -= self.base
        return network_data

    def _run(self):
        while True:
            network_data = self.new_bandwidth_difference()
            self.on_update(network_data)
            self.total_runs.append(network_data)
            time.sleep(self.interval)

    def start_session(self):
        thread = Thread(target=self._run, daemon=True)
        thread.start()

    def get_network_data(self):
        return self.total_runs

    def dump_session(self):
        try:
            os.mkdir("dumps")
        except Exception:
            pass

        filename = "bandwidth-monitor-{}".format(
            datetime.now().strftime("%Y-%m-%d_%H%M%S")
        )

        with open(f"dumps/{filename}", "w+", encoding="utf-8") as f:
            f.write(repr(self.base) + "\n")
            f.write(
                "\n".join(
                    repr(network_data) for network_data in self.get_network_data()
                )
            )
