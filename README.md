# ARANET Data Project

This project is designed to collect, analyze, and visualize data from Aranet4 devices, such as CO₂ levels, temperature, humidity, and pressure. The repository contains three main Python scripts, each handling different aspects of the pipeline: data fetching, statistical analysis, and data plotting.

---

## Files

### 1. `fetchData.py`

This script is responsible for:
- Fetching records from Aranet4 devices based on their MAC addresses.
- Storing the combined data in an SQLite database (`aranet4_data.db`).
- Exporting the data to a CSV file (`aranet4_data.csv`).

**Key Functionality**:
- `aranet4_to_db_append_and_csv()`: Fetches data from Aranet4 devices, updates the database, ensures no duplicates, and exports to a CSV file.

---

### 2. `statsData.py`

This script provides functionality for advanced data analysis and visualization, including:
- Sliding window analysis of changes in sensor data over time.
- Distribution plotting of absolute differences for each variable.

**Key Functions**:
- `plot_sliding_difference()`: Analyzes and visualizes absolute differences in data over a sliding window.
- `plot_distribution()`: Creates distribution plots to show the density of absolute differences for each variable.

---

### 3. `plotData.py`

This script focuses on plotting time-series data for the different variables from the Aranet4 devices. It retrieves the data from the SQLite database (`aranet4_data.db`) and creates a **2x2 grid of plots** for the following variables:
- CO₂ levels (`CO2 (ppm)`)
- Temperature (`Temperature (°C)`)
- Humidity (`Humidity (%)`)
- Pressure (`Pressure (hPa)`)

The generated plot is saved as `data_plot.png`.

---

## Getting Started

### Installation & Setup
1. Clone the repository:
   ```bash
   git clone git@github.com:stloufra/ARANET.git
   cd ARANET
   ```

2. Install required Python packages:
   ```bash
   pip install matplotlib pandas sqlite3 numpy aranet4
   ```

3. Setup your SQLite database (`aranet4_data.db`) by running `fetchData.py` with valid MAC addresses.

---

### Usage

1. **Fetch Data**:
   Run `fetchData.py` to collect data from the Aranet4 devices, update the database, and export it to CSV:
   ```bash
   python3 fetchData.py
   ```

2. **Analyze Data**:
   Use `statsData.py` to analyze data with sliding window differences or distributions:
   ```bash
   python3 statsData.py
   ```

3. **Visualize Data**:
   Generate time-series plots using `plotData.py`:
   ```bash
   python3 plotData.py
   ```

---

## Output

- **Database**: `aranet4_data.db`
- **CSV File**: `aranet4_data.csv`
- **Plots**:
    - Time-series plots (`data_plot.png`)
    - Distribution plots (`difference_distribution.png`)

---

## License

This project is open-source and available for use and modification. Ensure you follow all applicable licenses for dependencies.

---

If you need any help, feel free to ask!