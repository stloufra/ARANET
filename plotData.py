import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
import numpy as np


def plotdata(db_path, data_output_path):

    # Read data
    conn = sqlite3.connect(db_path)
    df = pd.read_sql("SELECT * FROM aranet4_data", conn, parse_dates=["Time"])
    conn.close()

    # Variables to plot
    variables = {
        "CO2 (ppm)": "CO₂ (ppm)",
        "Temperature (°C)": "Temperature (°C)",
        "Humidity (%)": "Humidity (%)",
        "Pressure (hPa)": "Pressure (hPa)"
    }

    device_ids = df["Device"].unique()
    colors = {dev: f"C{i}" for i, dev in enumerate(device_ids)}

    # Create 2x2 plot
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes_flat = axes.flatten()

    for i, (var, label) in enumerate(variables.items()):
        ax = axes_flat[i]

        # Plot each device individually
        for device in device_ids:
            dev_data = df[df["Device"] == device].sort_values("Time")  # Ensure sorted by time
            ax.plot(dev_data["Time"], dev_data[var], label=f"Device {device}", color=colors[device])

        ax.set_title(label)
        ax.set_xlabel("Time")
        ax.set_ylabel(label)
        ax.legend()
        fig.autofmt_xdate(rotation=30, ha="right")

    fig.tight_layout()
    plt.savefig(data_output_path)

if __name__ == "__main__":
    db_path = "aranet4_data.db"
    data_output_path = "data_plot.png"

    plotdata(db_path, data_output_path)
