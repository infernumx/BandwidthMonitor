import PySimpleGUI as sg
from bandwidth_monitor import BandwidthMonitor, ReferenceFlag, EasyElement
from dataclasses import dataclass

sg.theme("DarkAmber")


class DataLog:
    def __init__(self, monitor, activated: ReferenceFlag):
        layout = [
            [
                sg.Listbox(
                    values=monitor.get_network_data(), size=(55, 80), key="-DATA_LOG-"
                )
            ]
        ]
        self.window = sg.Window(
            "Data Log",
            layout,
            size=(430, 300),
            modal=True,
            finalize=True,
            element_justification="center",
        )

        self.activated = activated

    def main(self):
        self.activated.set()
        while True:
            event, values = self.window.read()
            if event == sg.WIN_CLOSED:
                self.activated.unset()
                break


class MainWindow:
    layout = [
        [EasyElement.CenterText("Sent"), EasyElement.CenterText("Received")],
        [
            EasyElement.CenterText("0.00 MB", key="-SENT_MB-"),
            EasyElement.CenterText("0.00 MB", key="-RECV_MB-"),
        ],
        [sg.Text("")],
        [
            sg.Button("Dump Session", key="-DUMP_SESSION-"),
            sg.Button("Data Log", key="-DATA_LOG_BTN-"),
        ],
    ]

    def __init__(self, monitor_interval):
        self.window = sg.Window(
            "Bandwidth Monitor",
            MainWindow.layout,
            size=(280, 120),
            finalize=True,
            element_justification="center",
        )

        self.data_log_flag = ReferenceFlag()
        self.data_log = None

        self.monitor = BandwidthMonitor(
            on_update=self.on_update, interval=monitor_interval
        )
        self.monitor.start_session()

        self.main()

    def on_update(self, network_data):
        self.window.Element("-SENT_MB-").update(f"{network_data.sent:.2f} MB")
        self.window.Element("-RECV_MB-").update(f"{network_data.received:.2f} MB")

        if self.data_log_flag.get():
            self.data_log.window.Element("-DATA_LOG-").update(
                values=self.monitor.get_network_data()
            )
            self.data_log.window.Element("-DATA_LOG-").set_vscroll_position(1)

    def main(self):
        while True:
            event, values = self.window.read()
            if event == sg.WIN_CLOSED:
                self.monitor.dump_session()
                break

            if event == "-DATA_LOG_BTN-":
                self.data_log = DataLog(self.monitor, self.data_log_flag)
                self.data_log.main()
            elif event == "-DUMP_SESSION-":
                self.monitor.dump_session()


MainWindow(monitor_interval=60)
