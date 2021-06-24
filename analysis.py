import easygui
import pandas as pd
import numpy as np
import streamlit as st
import altair as alt
from bandwidth_monitor import NetworkData
import datetime
import logging


def create_logger(
    name=None, stream=True, logfile=None, level=logging.INFO, propagate=False
):
    logger = logging.getLogger(name)
    formatter = logging.Formatter(
        fmt="[{asctime}] {levelname:<8} | {filename}:{lineno} -> {message}",
        datefmt="%Y-%m-%d %H:%M:%S",
        style="{",
    )

    if stream:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    if logfile:
        file_handler = logging.FileHandler(logfile, mode="w", encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    logger.setLevel(level)
    logger.propagate = propagate
    return logger


def process_dumpfile(filename):
    base_network_data: NetworkData = None
    last_threshold_data: NetworkData = None
    future: datetime.datetime = None
    hours = 1
    processed = {"sent": [], "recv": [], "aggr": {"sent": [], "recv": []}}

    with open(filename) as f:
        for line in f:
            network_data = eval(line)
            delta = datetime.timedelta(
                seconds=network_data.time.second,
                microseconds=network_data.time.microsecond,
            )

            if not base_network_data:
                base_network_data = network_data
                future = base_network_data.time + (
                    datetime.timedelta(0, hours=1) - delta
                )
                logger.info("Base network data: " + str(base_network_data))
                continue

            logger.info("Current network data: " + str(network_data))

            if network_data.time - delta > future:
                hours += 1
                processed["sent"].append(network_data.sent)
                processed["recv"].append(network_data.received)

                logger.info(f"Hour {hours} threshold reached")
                difference: NetworkData = None

                # Calculate difference in data from the last hour
                if last_threshold_data is None:
                    logger.info(f"Network data for the last hour: {network_data}")
                    difference = network_data
                else:
                    logger.info(f"Network data for the last hour: {difference}")
                    difference = network_data - last_threshold_data

                last_threshold_data = network_data

                # Reset data for next threshold
                future = base_network_data.time + (
                    datetime.timedelta(0, hours=hours) - delta
                )
                processed["aggr"]["sent"].append(difference.sent)
                processed["aggr"]["recv"].append(difference.received)

    return processed


def create_line_graph(data, y_axis):
    df = pd.DataFrame({y_axis: data, "Hours": [i for i in range(len(data))]})

    return alt.Chart(df).mark_line().encode(x="Hours", y=y_axis)


logger = create_logger("NetworkData", stream=False, logfile="NetworkData.log")
filename = easygui.fileopenbox()
processed = process_dumpfile(filename)

# Constant hourly data

sent, recv = processed["sent"], processed["recv"]
data_by_hour = list(zip(sent, recv))
data_length = len(data_by_hour)
fill = len(str(data_length))

df_hourly_data = pd.DataFrame(
    [{"Sent": sent, "Received": received} for sent, received in data_by_hour],
    index=[f"Hour {str(i).zfill(fill)}" for i in range(data_length)],
)

# Difference in data by hour

diff_sent, diff_recv = processed["aggr"]["sent"], processed["aggr"]["recv"]
diff_by_hour = list(zip(diff_sent, diff_recv))
data_length = len(diff_by_hour)
fill = len(str(data_length))

df_diff_data = pd.DataFrame(
    [{"Sent": sent, "Received": received} for sent, received in diff_by_hour],
    index=[f"Hour {str(i).zfill(fill)}" for i in range(data_length)],
)

# Streamlit UI setup

st.title("Bandwidth Monitor")

st.text("Hourly data usage")
st.line_chart(df_hourly_data)

sent_chart = create_line_graph(sent, "Sent data in MB")
recv_chart = create_line_graph(recv, "Received data in MB")

st.altair_chart(sent_chart | recv_chart)

st.text("Hourly data differences")
st.bar_chart(df_diff_data)
