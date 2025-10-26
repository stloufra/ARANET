import matplotlib.pyplot as plt
import aranet4 as a4
import pandas as pd
import sqlite3
import os


def aranet4_to_db_append_and_csv(device_macs, db_path="aranet4_data.db", csv_path="aranet4_data.csv"):
    """
    Fetches all Aranet4 records for given MACs, appends new data
    to an existing SQLite database, and exports the combined data to a .csv file.

    Parameters:
        device_macs (dict): {device_id: mac_address}
        db_path (str): path to SQLite database file
        csv_path (str): path to CSV file to export data
    Returns:
        df_all (pd.DataFrame): combined dataframe with all device data
    """
    # Try to read existing data
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        df_existing = pd.read_sql("SELECT * FROM aranet4_data", conn, parse_dates=["Time"])
        conn.close()
    else:
        df_existing = pd.DataFrame(columns=["Device", "MAC", "Time", "CO2 (ppm)",
                                            "Temperature (°C)", "Humidity (%)", "Pressure (hPa)"])

    # Fetch new records
    all_data = []
    for device_id, mac in device_macs.items():
        records = a4.client.get_all_records(mac, entry_filter={}).value
        for rec in records:
            all_data.append({
                "Device": device_id,
                "MAC": mac,
                "Time": rec.date,
                "CO2 (ppm)": rec.co2,
                "Temperature (°C)": rec.temperature,
                "Humidity (%)": rec.humidity,
                "Pressure (hPa)": rec.pressure
            })

    df_new = pd.DataFrame(all_data)

    # Remove duplicates already in the database
    if not df_existing.empty:
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        df_combined.drop_duplicates(subset=["Device", "Time"], inplace=True)
    else:
        df_combined = df_new

    # Save back to database
    conn = sqlite3.connect(db_path)
    df_combined.to_sql("aranet4_data", conn, if_exists="replace", index=False)
    conn.close()

    # Export data to CSV
    df_combined.to_csv(csv_path, index=False)
    print(f"Data appended to {db_path} and exported to {csv_path}, total records: {len(df_combined)}")
    return df_combined




if __name__ == "__main__":

    device_macs = {
        4: "CA:61:29:F1:70:9C",
        2: "C6:C8:4E:7B:CC:DA",
        1: "DC:5B:74:B8:A3:3E",
        3: "EF:52:FC:26:28:1D"
    }

    df_all = aranet4_to_db_append_and_csv(device_macs)
    print(df_all.tail())