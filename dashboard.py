import streamlit as st
import pandas as pd
import plotly.express as px
import random
import logging
import time
from PyQt5 import QtCore as qtc

# -----------------------------------------------
# CSS for compact layout and scaling
# -----------------------------------------------
st.markdown("""
    <style>
    .block-container {
        transform: scale(0.85);
        transform-origin: top center;
        padding-top: 0rem;
        padding-bottom: 0rem;
    }
    .stMetric {
        margin: 0;
        padding: 0;
    }
    .element-container iframe {
        height: 400px !important;
    }
    h1, .stCaption {
        display: none;  /* hide title/caption */
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------
# Logging setup
# -----------------------------------------------
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# -----------------------------------------------
# DummyLockIn Class
# -----------------------------------------------
class DummyLockIn(qtc.QObject):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.is_open = False

    def open(self):
        try:
            self.is_open = True
        except Exception as e:
            logger.error(f"Failed to connect to lock-in with {e}")

    def close(self):
        self.is_open = False

    def __del__(self):
        self.close()

    def acquire_channel(self):
        return random.uniform(20.0, 30.0)

# -----------------------------------------------
# Create 3 Sensors (3 Rooms)
# -----------------------------------------------
room_sensors = {
    "Room 1": DummyLockIn(),
    "Room 2": DummyLockIn(),
    "Room 3": DummyLockIn(),
}
for sensor in room_sensors.values():
    sensor.open()

# -----------------------------------------------
# Function to read latest sensor values
# -----------------------------------------------
def get_latest_data():
    readings = {}
    for room, sensor in room_sensors.items():
        temperature = sensor.acquire_channel()
        humidity = random.uniform(40.0, 70.0)
        readings[room] = {"temperature": temperature, "humidity": humidity}
    return readings

# -----------------------------------------------
# Streamlit Dashboard Setup
# -----------------------------------------------
st.set_page_config(page_title="Lab Dashboard", layout="wide")

if "history" not in st.session_state:
    st.session_state.history = []

# -----------------------------------------------
# Read latest data
# -----------------------------------------------
data = get_latest_data()
timestamp = pd.Timestamp.now()

flat = []
for room, values in data.items():
    flat.append([timestamp, room, values["temperature"], values["humidity"]])

st.session_state.history.extend(flat)
st.session_state.history = st.session_state.history[-100:]  # keep last 100 entries

df = pd.DataFrame(
    st.session_state.history,
    columns=["time", "room", "temperature", "humidity"],
)

# -----------------------------------------------
# Display Live Metrics (side by side)
# -----------------------------------------------
st.subheader("📡 Current Sensor Readings")
cols = st.columns(len(room_sensors))
for i, (room, values) in enumerate(data.items()):
    with cols[i]:
        st.metric(f"{room} Temperature (°C)", f"{values['temperature']:.2f}")
        st.metric(f"{room} Humidity (%)", f"{values['humidity']:.2f}")

# -----------------------------------------------
# Charts side by side
# -----------------------------------------------
st.subheader("📊 Trends")
col1, col2 = st.columns(2)

with col1:
    temp_fig = px.line(
        df,
        x="time",
        y="temperature",
        color="room",
        markers=True,
        title="Temperature Over Time",
    )
    temp_fig.update_layout(height=400)
    st.plotly_chart(temp_fig, use_container_width=True)

with col2:
    hum_fig = px.line(
        df,
        x="time",
        y="humidity",
        color="room",
        markers=True,
        title="Humidity Over Time",
    )
    hum_fig.update_layout(height=400)
    st.plotly_chart(hum_fig, use_container_width=True)

# -----------------------------------------------
# Auto-refresh with countdown
# -----------------------------------------------
refresh_interval = 30
countdown = st.empty()
for i in range(refresh_interval, 0, -1):
    countdown.markdown(f"⏳ Refreshing in **{i} seconds**...")
    time.sleep(1)

st.rerun()