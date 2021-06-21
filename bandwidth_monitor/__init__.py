from .monitor import BandwidthMonitor
from .network_data import NetworkData
from dataclasses import dataclass
import PySimpleGUI as sg


class EasyElement:
    @staticmethod
    def CenterText(txt, key=None):
        return sg.Text(txt, justification="center", size=(15, 1), key=key)


@dataclass
class ReferenceFlag:
    flag: bool = False

    def set(self):
        self.flag = True

    def unset(self):
        self.flag = False

    def get(self):
        return self.flag
