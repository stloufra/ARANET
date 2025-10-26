import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
import seaborn as sns

def plot_sliding_difference(db_path, start_time="2025-10-26 19:30", abs_output_path="sliding_difference.png",
                            rel_output_path="sliding_difference_relative.png",
                            data_output_path="sliding_difference_data.csv"):
    """
    Calculates the sliding difference and relative difference between each device's variable values
    and the mean of the closest 5 consecutive entries (centered) in time from device 1.
    Saves the data into a CSV file and plots the absolute and relative differences.

    Args:
        db_path (str): Path to the SQLite database file.
        start_time (str): The starting time for the plot (format: "YYYY-MM-DD HH:MM").
        abs_output_path (str): File path to save absolute difference plot.
        rel_output_path (str): File path to save relative difference plot.
        data_output_path (str): File path to save computed sliding differences.
    """
    # Convert start_time to a timezone-aware datetime object
    start_time = pd.to_datetime(start_time).tz_localize("UTC")

    # Read data from the database
    conn = sqlite3.connect(db_path)
    df = pd.read_sql("SELECT * FROM aranet4_data", conn, parse_dates=["Time"])
    conn.close()

    # Ensure that the Time column is timezone-aware
    if df["Time"].dt.tz is None:
        df["Time"] = df["Time"].dt.tz_localize("UTC")

    # Filter data to include only entries after the start_time
    df = df[df["Time"] >= start_time]

    # Variables to plot
    variables = {
        "CO2 (ppm)": "CO₂ (ppm)",
        "Temperature (°C)": "Temperature (°C)",
        "Humidity (%)": "Humidity (%)",
        "Pressure (hPa)": "Pressure (hPa)"
    }

    # Separate data for each device
    device_ids = df["Device"].unique()
    device_1_data = df[df["Device"] == 1].sort_values("Time")  # Data from device 1, sorted by time

    # Data to save into CSV
    all_differences = []

    # Initialize plots for absolute and relative differences
    fig_abs, axes_abs = plt.subplots(2, 2, figsize=(14, 10))
    axes_abs = axes_abs.flatten()
    fig_rel, axes_rel = plt.subplots(2, 2, figsize=(14, 10))
    axes_rel = axes_rel.flatten()

    for var_index, (var, label) in enumerate(variables.items()):
        ax_abs = axes_abs[var_index]
        ax_rel = axes_rel[var_index]

        # Prepare device 1 data for sliding window calculation
        dev1_var_data = device_1_data[["Time", var]].reset_index(drop=True)

        for device in device_ids:
            if device == 1:  # Skip device 1 since it's the reference
                continue

            # Data from the current device to compare
            dev_data = df[df["Device"] == device][["Time", var]].sort_values("Time").reset_index(drop=True)

            # Calculate sliding absolute and relative differences
            differences = []
            relative_differences = []

            for time in dev_data["Time"]:
                # Find the 5 closest entries in device 1 around the current time
                closest = dev1_var_data.iloc[
                    (dev1_var_data["Time"] - time).abs().argsort()[:5]
                ]
                mean_value = closest[var].mean()

                # Get the value for the current device at the current time
                current_value = dev_data[dev_data["Time"] == time]
                if not current_value.empty:
                    abs_difference = current_value[var].values[0] - mean_value
                    relative_difference = (abs_difference / mean_value) * 100 if mean_value != 0 else None
                    differences.append(
                        {"Time": time, "Device": device, "Variable": var, "Absolute Difference": abs_difference,
                         "Relative Difference (%)": relative_difference})
                    all_differences.append(
                        {"Time": time, "Device": device, "Variable": var, "Absolute Difference": abs_difference,
                         "Relative Difference (%)": relative_difference})

            # Convert differences to DataFrames for plotting
            diff_df = pd.DataFrame(differences)

            # Plot the sliding absolute difference
            ax_abs.plot(diff_df["Time"], diff_df["Absolute Difference"], label=f"Device {device}")

            # Plot the sliding relative difference (percentage)
            ax_rel.plot(diff_df["Time"], diff_df["Relative Difference (%)"], label=f"Device {device}")

        # Format the absolute difference plot
        ax_abs.set_title(f"Absolute Sliding Difference for {label}")
        ax_abs.set_xlabel("Time")
        ax_abs.set_ylabel(f"Absolute Difference ({label})")
        ax_abs.legend()
        ax_abs.grid(True)

        # Format the relative difference plot
        ax_rel.set_title(f"Relative Sliding Difference (Percentage) for {label}")
        ax_rel.set_xlabel("Time")
        ax_rel.set_ylabel(f"Relative Difference (%)")
        ax_rel.legend()
        ax_rel.grid(True)

    # Save collected data to CSV
    all_differences_df = pd.DataFrame(all_differences)
    all_differences_df.to_csv(data_output_path, index=False)
    print(f"Sliding difference data saved to {data_output_path}")

    # Adjust layouts and save the plots
    fig_abs.tight_layout()
    fig_abs.savefig(abs_output_path)
    print(f"Absolute sliding difference plot saved to {abs_output_path}")
    fig_rel.tight_layout()
    fig_rel.savefig(rel_output_path)
    print(f"Relative sliding difference plot saved to {rel_output_path}")
    #plt.show()


def plot_distribution(data_path, output_path="difference_distribution.png"):
    """
    Plots the distribution of differences for each variable in 2x2 subplots.
    Each variable has its own subplot; device curves overlap, with transparency.

    Args:
        data_path (str): Path to the CSV file containing sliding difference data.
        output_path (str): File path to save the distribution plot.
    """
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns  # Import Seaborn for distribution plots

    # Read sliding difference data from the CSV
    data = pd.read_csv(data_path)

    # Variables to plot
    variables = data["Variable"].unique()

    # Initialize 2x2 plot grid
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()

    for idx, var in enumerate(variables):
        ax = axes[idx]

        # Get subset of data for the current variable
        subset = data[data["Variable"] == var]
        device_ids = subset["Device"].unique()

        # Plot density for each device
        for device in device_ids:
            device_data = subset[subset["Device"] == device]

            # Plot the density (kernel density estimate) with transparency for the area
            if not device_data.empty:
                sns.kdeplot(
                    device_data["Absolute Difference"],
                    ax=ax,
                    fill=True,
                    label=f"Device {device}",
                    alpha=0.4
                )

        # Set plot titles and labels
        ax.set_title(f"Distribution of {var}")
        ax.set_xlabel("Absolute Difference")
        ax.set_ylabel("Density")
        ax.legend()
        ax.grid(True)

    # Remove any unused subplots if variables < 4
    for ax in axes[len(variables):]:
        fig.delaxes(ax)

    # Adjust layout and save the plot
    fig.tight_layout()
    plt.savefig(output_path)
    print(f"Distribution plot saved to {output_path}")
#    plt.show()



if __name__ == "__main__":
    db_path = "aranet4_data.db"
    data_output_path = "sliding_difference_data.csv"

    # Generate sliding differences and save data
    plot_sliding_difference(db_path, start_time="2025-10-26 19:30", data_output_path=data_output_path)

    # Plot distribution
    plot_distribution(data_path=data_output_path)