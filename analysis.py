import easygui
import pandas as pd
import numpy as np
import streamlit as st
import altair as alt
from bandwidth_monitor import NetworkData
import datetime

filename = easygui.fileopenbox()
data_by_hour = [[0, 0]]


def process_dumpfile(filename):
    base: NetworkData = None
    ndata: NetworkData = None
    future: datetime.datetime = None
    hours = 1
    sent = []
    recv = []

    with open(filename) as f:
        for line in f:
            network_data = eval(line)
            delta = datetime.timedelta(
                seconds=network_data.time.second,
                microseconds=network_data.time.microsecond,
            )
            if not base:
                base = network_data
                future = base.time + (datetime.timedelta(0, hours=1) - delta)
                continue

            if network_data.time - delta > future:
                sent.append(network_data.sent)
                recv.append(network_data.received)
                hours += 1
                future = base.time + (datetime.timedelta(0, hours=hours) - delta)

    return sent, recv


def create_line_graph(data, y_axis):
    df = pd.DataFrame({y_axis: data, "Hours": [i for i in range(len(data))]})

    return alt.Chart(df).mark_line().encode(x="Hours", y=y_axis)


sent, recv = process_dumpfile(filename)
data_by_hour = list(zip(sent, recv))

st.title("Bandwidth Monitor")

data = [{"Sent": sent, "Received": received} for sent, received in data_by_hour]

data_length = len(data_by_hour)
fill = len(str(data_length))

df = pd.DataFrame(
    data, index=[f"Hour {str(i).zfill(fill)}" for i in range(data_length)]
)
st.line_chart(df)

sent_chart = create_line_graph(sent, "Sent data in MB")
recv_chart = create_line_graph(recv, "Received data in MB")

st.altair_chart(sent_chart | recv_chart)
