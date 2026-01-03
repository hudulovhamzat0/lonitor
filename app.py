import sys
import psutil
import subprocess
import shutil
import os
import signal
from PyQt6.QtCore import QMargins
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QProgressBar, QPushButton,
    QHBoxLayout, QComboBox, QGroupBox, QGridLayout, QTabWidget, QTextEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QFrame
)
from PyQt6.QtCore import QTimer, Qt, QSize
from PyQt6.QtGui import QFont, QPalette, QColor, QPainter, QIcon
from PyQt6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis

# --- Helper Functions ---

def get_cpu_temp():
    """Get CPU temperature from thermal zone"""
    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            temp = int(f.read().strip()) / 1000
            return temp
    except:
        return 0.0

def clear_ram_cache():
    """Clear system RAM cache (requires sudo)"""
    try:
        subprocess.run(["sudo", "sh", "-c", "sync; echo 3 > /proc/sys/vm/drop_caches"], check=True)
        return True, "RAM cache cleared successfully!"
    except Exception as e:
        return False, f"Failed to clear RAM cache: {str(e)}"

def clear_storage_cache():
    """Clear temporary files and cache directories"""
    try:
        subprocess.run(["sudo", "rm", "-rf", "/tmp/*"], shell=True, check=False)
        home_cache = os.path.expanduser("~/.cache")
        if os.path.exists(home_cache):
            for item in os.listdir(home_cache):
                item_path = os.path.join(home_cache, item)
                try:
                    if os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                    else:
                        os.remove(item_path)
                except:
                    pass
        return True, "Storage caches cleared successfully!"
    except Exception as e:
        return False, f"Failed to clear storage cache: {str(e)}"

def set_power_mode(mode):
    """Set system power profile"""
    try:
        subprocess.run(["sudo", "powerprofilesctl", "set", mode], check=True)
        return True, f"Power mode set to {mode}"
    except Exception as e:
        return False, f"Failed to set power mode: {str(e)}"

def kill_process(pid):
    """Kill a process by PID"""
    try:
        os.kill(pid, signal.SIGTERM)
        return True, f"Process {pid} terminated successfully"
    except ProcessLookupError:
        return False, f"Process {pid} not found"
    except PermissionError:
        return False, f"Permission denied to kill process {pid}"
    except Exception as e:
        return False, f"Failed to kill process: {str(e)}"

def get_battery_info():
    """Get detailed battery information"""
    battery = psutil.sensors_battery()
    if battery:
        charging = "Charging" if battery.power_plugged else "Discharging"
        percent = battery.percent
        secs_left = battery.secsleft
        if secs_left == psutil.POWER_TIME_UNLIMITED:
            time_str = "Plugged In"
        elif secs_left == psutil.POWER_TIME_UNKNOWN:
            time_str = "Calculating..."
        else:
            hrs = secs_left // 3600
            mins = (secs_left % 3600) // 60
            time_str = f"{hrs}h {mins}m"
        return {
            'status': charging,
            'percent': percent,
            'time': time_str,
            'plugged': battery.power_plugged
        }
    return None

def get_disk_info():
    """Get disk usage information"""
    usage = psutil.disk_usage('/')
    return {
        'total': usage.total / (1024 ** 3),
        'used': usage.used / (1024 ** 3),
        'free': usage.free / (1024 ** 3),
        'percent': usage.percent
    }

def get_network_info():
    """Get network statistics"""
    net = psutil.net_io_counters()
    return {
        'sent': net.bytes_sent / (1024 ** 2),
        'recv': net.bytes_recv / (1024 ** 2)
    }

def get_top_processes(limit=10):
    """Get top processes by CPU usage"""
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            processes.append(proc.info)
        except:
            pass
    return sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:limit]


# --- Styled Components ---

class MetricCard(QGroupBox):
    """A styled card for displaying metrics"""
    def __init__(self, title):
        super().__init__(title)
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 15px;
                background-color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #1976D2;
            }
        """)


class StyledProgressBar(QProgressBar):
    """A modern styled progress bar"""
    def __init__(self):
        super().__init__()
        self.setTextVisible(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumHeight(25)
        self.setStyleSheet("""
            QProgressBar {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                text-align: center;
                background-color: #f5f5f5;
                font-weight: bold;
            }
            QProgressBar::chunk {
                border-radius: 6px;
                background-color: #4CAF50;
            }
        """)
    
    def update_color(self, value):
        """Update color based on value"""
        if value < 60:
            color = "#4CAF50"
        elif value < 85:
            color = "#FF9800"
        else:
            color = "#F44336"
        
        self.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                text-align: center;
                background-color: #f5f5f5;
                font-weight: bold;
            }}
            QProgressBar::chunk {{
                border-radius: 6px;
                background-color: {color};
            }}
        """)


class StyledButton(QPushButton):
    """A modern styled button"""
    def __init__(self, text, color="#1976D2"):
        super().__init__(text)
        self.color = color
        self.setMinimumHeight(35)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.update_style()
    
    def update_style(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.color};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {self.darken_color(self.color)};
            }}
            QPushButton:pressed {{
                background-color: {self.darken_color(self.color, 0.8)};
            }}
        """)
    
    def darken_color(self, hex_color, factor=0.85):
        """Darken a hex color"""
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r, g, b = int(r * factor), int(g * factor), int(b * factor)
        return f"#{r:02x}{g:02x}{b:02x}"


# --- Main GUI ---

class EnhancedSysMonitor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lonitor")
        self.resize(950, 900)
        self.setup_styles()
        self.setup_ui()
        
        self.x = 0
        self.network_baseline = get_network_info()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(1000)

    def setup_styles(self):
        """Setup application-wide styles"""
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QTabWidget::pane {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                background-color: white;
                top: -2px;
            }
            QTabBar::tab {
                background-color: #e8eaf6;
                color: #1976D2;
                border: 2px solid #e0e0e0;
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                padding: 10px 20px;
                margin-right: 2px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid white;
            }
            QTabBar::tab:hover {
                background-color: #c5cae9;
            }
            QLabel {
                color: #333;
                font-size: 13px;
            }
            QComboBox {
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                padding: 6px;
                background-color: white;
                min-height: 25px;
            }
            QComboBox:hover {
                border-color: #1976D2;
            }
            QTableWidget {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                background-color: white;
                gridline-color: #e0e0e0;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976D2;
            }
            QHeaderView::section {
                background-color: #1976D2;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
            QTextEdit {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                background-color: #263238;
                color: #4CAF50;
                font-family: 'Courier New', monospace;
                padding: 8px;
            }
        """)

    def setup_ui(self):
        """Initialize UI components"""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        self.setLayout(main_layout)
        
        # Title
        title = QLabel("⚡ Lonitor")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #1976D2; padding: 10px;")
        main_layout.addWidget(title)
        
        # Create tabs
        tabs = QTabWidget()
        main_layout.addWidget(tabs)
        
        # Overview Tab
        overview_tab = QWidget()
        overview_layout = QVBoxLayout()
        overview_layout.setSpacing(12)
        overview_layout.setContentsMargins(15, 15, 15, 15)
        overview_tab.setLayout(overview_layout)
        self.setup_overview_tab(overview_layout)
        tabs.addTab(overview_tab, "📊 Overview")
        
        # Processes Tab
        processes_tab = QWidget()
        processes_layout = QVBoxLayout()
        processes_layout.setSpacing(12)
        processes_layout.setContentsMargins(15, 15, 15, 15)
        processes_tab.setLayout(processes_layout)
        self.setup_processes_tab(processes_layout)
        tabs.addTab(processes_tab, "⚙️ Processes")
        
        # System Actions Tab
        actions_tab = QWidget()
        actions_layout = QVBoxLayout()
        actions_layout.setSpacing(12)
        actions_layout.setContentsMargins(15, 15, 15, 15)
        actions_tab.setLayout(actions_layout)
        self.setup_actions_tab(actions_layout)
        tabs.addTab(actions_tab, "🔧 Actions")

    def setup_overview_tab(self, layout):
        """Setup the overview tab"""
        
        # Top row: CPU and RAM
        top_row = QHBoxLayout()
        top_row.setSpacing(10)
        
        # CPU Card
        cpu_card = MetricCard("🖥️ CPU")
        cpu_layout = QVBoxLayout()
        cpu_layout.setSpacing(8)
        cpu_card.setLayout(cpu_layout)
        
        self.cpu_label = QLabel("Usage: 0%")
        self.cpu_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.cpu_bar = StyledProgressBar()
        self.cpu_temp_label = QLabel("🌡️ Temperature: 0°C")
        
        cpu_layout.addWidget(self.cpu_label)
        cpu_layout.addWidget(self.cpu_bar)
        cpu_layout.addWidget(self.cpu_temp_label)
        
        self.cpu_series = QLineSeries()
        self.cpu_chart_view = self.create_chart_view(self.cpu_series, "CPU %", "#1976D2")
        cpu_layout.addWidget(self.cpu_chart_view)
        
        top_row.addWidget(cpu_card)
        
        # RAM Card
        ram_card = MetricCard("💾 Memory")
        ram_layout = QVBoxLayout()
        ram_layout.setSpacing(8)
        ram_card.setLayout(ram_layout)
        
        self.ram_label = QLabel("Usage: 0%")
        self.ram_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.ram_bar = StyledProgressBar()
        self.ram_details = QLabel("0 GB / 0 GB")
        
        ram_layout.addWidget(self.ram_label)
        ram_layout.addWidget(self.ram_bar)
        ram_layout.addWidget(self.ram_details)
        
        self.ram_series = QLineSeries()
        self.ram_chart_view = self.create_chart_view(self.ram_series, "RAM %", "#4CAF50")
        ram_layout.addWidget(self.ram_chart_view)
        
        top_row.addWidget(ram_card)
        layout.addLayout(top_row)
        
        # Bottom row: Disk, Network, Battery
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(10)
        
        # Disk Card
        disk_card = MetricCard("💿 Disk")
        disk_layout = QVBoxLayout()
        disk_layout.setSpacing(8)
        disk_card.setLayout(disk_layout)
        self.disk_label = QLabel("Loading...")
        self.disk_bar = StyledProgressBar()
        disk_layout.addWidget(self.disk_label)
        disk_layout.addWidget(self.disk_bar)
        bottom_row.addWidget(disk_card)
        
        # Network Card
        network_card = MetricCard("🌐 Network")
        network_layout = QVBoxLayout()
        network_layout.setSpacing(5)
        network_card.setLayout(network_layout)
        self.network_sent_label = QLabel("⬆️ Sent: 0 MB")
        self.network_recv_label = QLabel("⬇️ Received: 0 MB")
        network_layout.addWidget(self.network_sent_label)
        network_layout.addWidget(self.network_recv_label)
        bottom_row.addWidget(network_card)
        
        # Battery Card
        battery_card = MetricCard("🔋 Battery")
        battery_layout = QVBoxLayout()
        battery_layout.setSpacing(8)
        battery_card.setLayout(battery_layout)
        self.battery_label = QLabel("Status: N/A")
        self.battery_bar = StyledProgressBar()
        battery_layout.addWidget(self.battery_label)
        battery_layout.addWidget(self.battery_bar)
        bottom_row.addWidget(battery_card)
        
        layout.addLayout(bottom_row)
        
        # System Uptime
        self.uptime_label = QLabel("⏱️ System Uptime: Calculating...")
        self.uptime_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.uptime_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 10px;")
        layout.addWidget(self.uptime_label)

    def setup_processes_tab(self, layout):
        """Setup the processes monitoring tab"""
        
        header_layout = QHBoxLayout()
        label = QLabel("📋 Active Processes")
        label_font = QFont()
        label_font.setPointSize(14)
        label_font.setBold(True)
        label.setFont(label_font)
        label.setStyleSheet("color: #1976D2;")
        header_layout.addWidget(label)
        
        header_layout.addStretch()
        
        self.kill_process_btn = StyledButton("🗑️ End Process", "#F44336")
        self.kill_process_btn.clicked.connect(self.kill_selected_process)
        header_layout.addWidget(self.kill_process_btn)
        
        layout.addLayout(header_layout)
        
        self.process_table = QTableWidget()
        self.process_table.setColumnCount(4)
        self.process_table.setHorizontalHeaderLabels(["PID", "Process Name", "CPU %", "Memory %"])
        self.process_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.process_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.process_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.process_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.process_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.process_table.setAlternatingRowColors(True)
        layout.addWidget(self.process_table)

    def setup_actions_tab(self, layout):
        """Setup the system actions tab"""
        
        # Power Profile
        power_card = MetricCard("⚡ Power Management")
        power_layout = QVBoxLayout()
        power_layout.setSpacing(10)
        power_card.setLayout(power_layout)
        
        power_selector_layout = QHBoxLayout()
        power_label = QLabel("Power Profile:")
        power_label.setStyleSheet("font-weight: bold;")
        self.power_combo = QComboBox()
        self.power_combo.addItems(["performance", "balanced", "power-saver"])
        self.power_combo.setCurrentText("balanced")
        self.power_apply_btn = StyledButton("Apply")
        self.power_apply_btn.clicked.connect(self.apply_power_mode)
        self.power_combo.setStyleSheet("""
    QComboBox {
        color: black;           /* text color when not expanded */
        font-weight: normal;
    }
    QComboBox QAbstractItemView {
        color: black;           /* text color in the dropdown list */
        selection-background-color: #1976D2;  /* optional: selected item bg */
        selection-color: white;               /* optional: selected item text */
    }
""")

        power_selector_layout.addWidget(power_label)
        power_selector_layout.addWidget(self.power_combo, 1)
        power_selector_layout.addWidget(self.power_apply_btn)
        power_layout.addLayout(power_selector_layout)
        
        layout.addWidget(power_card)
        
        # Cache Management
        cache_card = MetricCard("🧹 Cache Management")
        cache_layout = QVBoxLayout()
        cache_layout.setSpacing(10)
        cache_card.setLayout(cache_layout)
        
        cache_info = QLabel("Clear system caches to free up memory and storage space.\n⚠️ Note: Requires sudo privileges.")
        cache_info.setWordWrap(True)
        cache_layout.addWidget(cache_info)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        self.clear_ram_btn = StyledButton("Clear RAM Cache", "#FF9800")
        self.clear_ram_btn.clicked.connect(self.clear_ram_cache_action)
        self.clear_storage_btn = StyledButton("Clear Storage Cache", "#FF9800")
        self.clear_storage_btn.clicked.connect(self.clear_storage_cache_action)
        
        btn_layout.addWidget(self.clear_ram_btn)
        btn_layout.addWidget(self.clear_storage_btn)
        cache_layout.addLayout(btn_layout)
        
        layout.addWidget(cache_card)
        
        # Log Output
        log_card = MetricCard("📜 Action Log")
        log_layout = QVBoxLayout()
        log_layout.setSpacing(5)
        log_card.setLayout(log_layout)
        
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMinimumHeight(150)
        log_layout.addWidget(self.log_output)
        
        layout.addWidget(log_card)

    def create_chart_view(self, series, y_label, color):
        """Create a styled chart view"""
        chart = QChart()
        chart.addSeries(series)
        chart.legend().hide()
        chart.setBackgroundRoundness(8)
        chart.setMargins(QMargins(0, 0, 0, 0))
        
        # Apply color to series
        pen = series.pen()
        pen.setWidth(3)
        pen.setColor(QColor(color))
        series.setPen(pen)
        
        axis_x = QValueAxis()
        axis_x.setRange(0, 60)
        axis_x.setLabelFormat("%d")
        axis_x.setTitleText("Seconds")
        axis_x.setGridLineVisible(False)
        
        axis_y = QValueAxis()
        axis_y.setRange(0, 100)
        axis_y.setTitleText(y_label)
        axis_y.setGridLineVisible(True)
        
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_x)
        series.attachAxis(axis_y)
        
        series.axis_x = axis_x
        series.axis_y = axis_y
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        chart_view.setMinimumHeight(180)
        chart_view.setMaximumHeight(180)
        
        return chart_view

    def update_stats(self):
        """Update all system statistics"""
        cpu = psutil.cpu_percent()
        ram_info = psutil.virtual_memory()
        temp = get_cpu_temp()
        battery_info = get_battery_info()
        disk_info = get_disk_info()
        network_info = get_network_info()
        
        # Update CPU
        self.cpu_label.setText(f"Usage: {cpu:.1f}%")
        self.cpu_temp_label.setText(f"🌡️ Temperature: {temp:.1f}°C")
        self.cpu_bar.setValue(int(cpu))
        self.cpu_bar.update_color(cpu)
        
        # Update RAM
        ram_percent = ram_info.percent
        ram_used = ram_info.used / (1024 ** 3)
        ram_total = ram_info.total / (1024 ** 3)
        self.ram_label.setText(f"Usage: {ram_percent:.1f}%")
        self.ram_details.setText(f"{ram_used:.1f} GB / {ram_total:.1f} GB")
        self.ram_bar.setValue(int(ram_percent))
        self.ram_bar.update_color(ram_percent)
        
        # Update Disk
        self.disk_label.setText(
            f"{disk_info['used']:.1f} GB / {disk_info['total']:.1f} GB"
        )
        self.disk_bar.setValue(int(disk_info['percent']))
        self.disk_bar.update_color(disk_info['percent'])
        
        # Update Network
        net_sent = network_info['sent'] - self.network_baseline['sent']
        net_recv = network_info['recv'] - self.network_baseline['recv']
        self.network_sent_label.setText(f"⬆️ Sent: {net_sent:.1f} MB")
        self.network_recv_label.setText(f"⬇️ Received: {net_recv:.1f} MB")
        
        # Update Battery
        if battery_info:
            self.battery_label.setText(
                f"{battery_info['status']} - {battery_info['percent']:.0f}%"
            )
            self.battery_bar.setValue(int(battery_info['percent']))
            self.battery_bar.update_color(100 - battery_info['percent'] if not battery_info['plugged'] else 0)
        else:
            self.battery_label.setText("No battery detected")
            self.battery_bar.setValue(0)
        
        # Update Uptime
        uptime_seconds = int(datetime.now().timestamp() - psutil.boot_time())
        uptime_hours = uptime_seconds // 3600
        uptime_minutes = (uptime_seconds % 3600) // 60
        self.uptime_label.setText(f"⏱️ System Uptime: {uptime_hours}h {uptime_minutes}m")
        
        # Update Charts
        self.cpu_series.append(self.x, cpu)
        self.ram_series.append(self.x, ram_percent)
        self.x += 1
        
        if self.cpu_series.count() > 60:
            self.cpu_series.remove(0)
        if self.ram_series.count() > 60:
            self.ram_series.remove(0)
        
        self.cpu_series.axis_x.setRange(max(0, self.x - 60), self.x)
        self.ram_series.axis_x.setRange(max(0, self.x - 60), self.x)
        
        # Update process table
        self.update_process_table()

    def update_process_table(self):
        """Update the process table with top processes"""
        processes = get_top_processes(10)
        self.process_table.setRowCount(len(processes))
        
        for i, proc in enumerate(processes):
            self.process_table.setItem(i, 0, QTableWidgetItem(str(proc['pid'])))
            self.process_table.setItem(i, 1, QTableWidgetItem(proc['name']))
            self.process_table.setItem(i, 2, QTableWidgetItem(f"{proc['cpu_percent']:.1f}"))
            self.process_table.setItem(i, 3, QTableWidgetItem(f"{proc['memory_percent']:.1f}"))

    def kill_selected_process(self):
        """Kill the selected process"""
        selected_items = self.process_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a process to terminate.")
            return
        
        row = selected_items[0].row()
        pid = int(self.process_table.item(row, 0).text())
        process_name = self.process_table.item(row, 1).text()
        
        reply = QMessageBox.question(
            self, 
            "Confirm Termination",
            f"Are you sure you want to terminate process:\n\n{process_name} (PID: {pid})?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success, message = kill_process(pid)
            self.log_message(message)
            if success:
                QMessageBox.information(self, "Success", message)
            else:
                QMessageBox.warning(self, "Error", message)

    def apply_power_mode(self):
        """Apply selected power mode"""
        mode = self.power_combo.currentText()
        success, message = set_power_mode(mode)
        self.log_message(message)
        if success:
            QMessageBox.information(self, "Success", message)
        else:
            QMessageBox.warning(self, "Error", message)

    def clear_ram_cache_action(self):
        """Clear RAM cache with feedback"""
        success, message = clear_ram_cache()
        self.log_message(message)
        if success:
            QMessageBox.information(self, "Success", message)
        else:
            QMessageBox.warning(self, "Error", message)

    def clear_storage_cache_action(self):
        """Clear storage cache with feedback"""
        success, message = clear_storage_cache()
        self.log_message(message)
        if success:
            QMessageBox.information(self, "Success", message)
        else:
            QMessageBox.warning(self, "Error", message)

    def log_message(self, message):
        """Add message to log output"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_output.append(f"[{timestamp}] {message}")


# --- Run App ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = EnhancedSysMonitor()
    window.show()
    sys.exit(app.exec())