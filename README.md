# Lonitor ⚡

A modern, feature-rich system monitoring application built with PyQt6 for Linux systems. Monitor your system's performance in real-time with an intuitive and beautiful interface.

![Lonitor](https://github.com/hudulovhamzat0/lonitor/blob/main/ss1.png?raw=true)

## Features

### 📊 Real-Time Monitoring
- **CPU Usage**: Track CPU utilization with live graphs and temperature monitoring
- **Memory (RAM)**: Monitor RAM usage with detailed statistics
- **Disk Usage**: View storage consumption and available space
- **Network Activity**: Track data sent and received
- **Battery Status**: Monitor battery level and charging status (for laptops)
- **System Uptime**: Display how long your system has been running

### ⚙️ Process Management
- View top processes by CPU usage
- Monitor CPU and memory usage per process
- Terminate processes directly from the interface
- Real-time process table updates

### 🔧 System Actions
- **Power Management**: Switch between performance, balanced, and power-saver modes
- **Cache Cleaning**: Clear RAM and storage caches to free up resources
- **Action Logging**: Track all system actions with timestamped logs

### 📈 Visual Analytics
- Live CPU and RAM usage charts
- Color-coded progress bars (green → orange → red)
- Clean, modern Material Design-inspired interface
- Tabbed layout for organized information

## Screenshots

### Overview Tab
![Overview Tab](https://github.com/hudulovhamzat0/lonitor/blob/main/ss1.png?raw=true)

The Overview tab provides a comprehensive dashboard of your system's vital statistics, including live graphs for CPU and RAM usage, along with instant updates for disk, network, and battery status.

### Processes Tab
![Processes Tab](https://github.com/hudulovhamzat0/lonitor/blob/main/ss2.png?raw=true)

The Processes tab displays the top 10 processes by CPU usage, allowing you to monitor resource consumption and terminate processes that are consuming too many resources.

### Actions Tab
![Actions Tab](https://github.com/hudulovhamzat0/lonitor/blob/main/ss3.png?raw=true)

The Actions tab gives you control over power profiles and system cache management, with a detailed action log showing the results of your operations.

## Installation

### Prerequisites

- Python 3.8 or higher
- Linux-based operating system
- Sudo privileges (for advanced features like cache clearing and power management)

### Setup

1. **Clone or download the repository**
   ```bash
   cd ~/Desktop
   mkdir SystemMonitorPro
   cd SystemMonitorPro
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install PyQt6 PyQt6-Charts psutil
   ```

4. **Run the application**
   
   For monitoring only (no sudo required):
   ```bash
   python app.py
   ```
   
   For full functionality including cache clearing and power management:
   ```bash
   sudo ./venv/bin/python app.py
   ```

## Usage

### Basic Monitoring
Simply run the application to start monitoring your system. The interface updates every second with the latest statistics.

### Process Management
1. Navigate to the **Processes** tab
2. Select a process from the table
3. Click **End Process** to terminate it
4. Confirm the action in the dialog box

### Power Management
1. Go to the **Actions** tab
2. Select your desired power profile from the dropdown:
   - **Performance**: Maximum performance, higher power consumption
   - **Balanced**: Balance between performance and power saving
   - **Power-saver**: Optimize for battery life
3. Click **Apply** to change the power profile

### Cache Cleaning
1. Navigate to the **Actions** tab
2. Click **Clear RAM Cache** to free up memory
3. Click **Clear Storage Cache** to remove temporary files
4. Check the Action Log for results

## Requirements

### Python Packages
- `PyQt6` - GUI framework
- `PyQt6-Charts` - For live charts and graphs
- `psutil` - System and process utilities

### System Requirements
- Linux kernel with `/sys/class/thermal/thermal_zone0/temp` for CPU temperature
- `powerprofilesctl` for power management (optional)
- Sudo access for cache clearing and power profile changes

## Troubleshooting

### ModuleNotFoundError: No module named 'PyQt6.QtCharts'
Install the Charts package separately:
```bash
pip install PyQt6-Charts
```

### Permission denied when running with sudo
Use the full path to your virtual environment's Python:
```bash
sudo /path/to/your/venv/bin/python app.py
```

### Cache clearing fails
Ensure you're running the application with sudo privileges:
```bash
sudo ./venv/bin/python app.py
```

### Power profile changes don't work
Make sure `powerprofilesctl` is installed:
```bash
sudo apt install power-profiles-daemon
```

### CPU temperature shows 0°C
Your system might not expose temperature through the standard thermal zone. This is normal for some systems and won't affect other monitoring features.

## Features Overview

| Feature | Requires Sudo | Description |
|---------|---------------|-------------|
| CPU Monitoring | ❌ No | Real-time CPU usage and temperature |
| RAM Monitoring | ❌ No | Memory usage and availability |
| Disk Monitoring | ❌ No | Storage space and usage |
| Network Monitoring | ❌ No | Data sent and received |
| Battery Monitoring | ❌ No | Battery level and status |
| Process List | ❌ No | View running processes |
| Kill Process | ⚠️ Sometimes | Depends on process ownership |
| Clear RAM Cache | ✅ Yes | Requires elevated privileges |
| Clear Storage Cache | ✅ Yes | Requires elevated privileges |
| Power Profile | ✅ Yes | Requires elevated privileges |

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests to improve the application.

## License

This project is open source and available for personal and educational use.

## Acknowledgments

- Built with [PyQt6](https://www.riverbankcomputing.com/software/pyqt/)
- System monitoring powered by [psutil](https://github.com/giampaolo/psutil)
- Inspired by modern Material Design principles

---

**Made with ❤️ for the Linux community**
