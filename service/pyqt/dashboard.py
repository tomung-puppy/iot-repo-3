import serial
import threading
import time
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6 import uic
from PyQt6.QtCore import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from collections import deque

from_class = uic.loadUiType("service/pyqt/dashboard.ui")[0]

# Define serial port configurations
# Adjust the COM port based on your environment
SERIAL_PORTS = {
    'ele_00': '/com',
    'ent_00': 'COM4',
    'cur_00': '/dev/ttyACM0',
    'dht_00': 'COM6',
}

# 그래프를 그리는 캔버스 클래스
class GraphCanvas(FigureCanvas):
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(8, 6))
        super().__init__(self.fig)
        self.setParent(parent)
        
        self.ax1 = self.fig.add_subplot(111)
        self.ax2 = self.ax1.twinx()
        
        self.max_points = 50
        self.temp_data = deque(maxlen=self.max_points)
        self.hum_data = deque(maxlen=self.max_points)
        self.index_data = deque(maxlen=self.max_points)
        self.current_index = 0
        
        self.setup_plot()
        
    def setup_plot(self):
        self.ax1.clear()
        self.ax2.clear()
        
        self.ax1.tick_params(axis='y', labelcolor='red')
        self.ax1.set_ylim(0, 35)
        self.ax1.grid(True, alpha=0.3)
        
        self.ax2.tick_params(axis='y', labelcolor='blue')
        self.ax2.set_ylim(0, 100)
        
        self.ax1.set_xticks([])
        
        self.fig.tight_layout()
        
    def update_graph(self, temperature, humidity):
        self.index_data.append(self.current_index)
        self.temp_data.append(temperature)
        self.hum_data.append(humidity)
        self.current_index += 1
        
        self.ax1.clear()
        self.ax2.clear()
        
        line1 = self.ax1.plot(list(self.index_data), list(self.temp_data), 
                             'r-o', linewidth=2, markersize=4, label='Temperature')
        self.ax1.tick_params(axis='y', labelcolor='red')
        self.ax1.set_ylim(0, 35)
        self.ax1.grid(True, alpha=0.3)
        
        line2 = self.ax2.plot(list(self.index_data), list(self.hum_data), 
                             'b-o', linewidth=2, markersize=4, label='Humidity')
        self.ax2.tick_params(axis='y', labelcolor='blue')
        self.ax2.set_ylim(0, 100)
        
        self.ax1.set_xticks([])
                
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        self.ax1.legend(lines, labels, loc='upper left', fontsize=9)
        
        self.fig.tight_layout()
        self.draw()


class SerialThread(QThread):
    received_data = pyqtSignal(str, str)  # port_name, data

    def __init__(self, serial_port, baud_rate):
        super().__init__()
        self.serial_port = serial_port
        self.baud_rate = baud_rate
        self.ser = None
        self.running = False

    def run(self):
        try:
            self.ser = serial.Serial(self.serial_port, self.baud_rate, timeout=1)
            self.running = True
            while self.running:
                if self.ser.in_waiting > 0:
                    data = self.ser.readline().decode('utf-8', errors='ignore').strip()
                    if data:
                        self.received_data.emit(self.serial_port, data)
                time.sleep(0.01)
        except serial.SerialException as e:
            print(f"Serial Error on {self.serial_port}: {e}")
        finally:
            if self.ser and self.ser.is_open:
                self.ser.close()

    def stop(self):
        self.running = False
        self.wait()

    def write(self, data):
        if self.ser and self.ser.is_open:
            self.ser.write(data.encode('utf-8'))

class WindowClass(QMainWindow, from_class) :
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.serial_threads = {}
        self.init_serial_ports()

        # 그래프 캔버스 생성 및 추가
        self.graph_canvas = GraphCanvas()
        layout = QVBoxLayout(self.widget_graph)
        layout.addWidget(self.graph_canvas)
        self.widget_graph.setLayout(layout)

        # Connect buttons to slots
        self.pushButton_1f.clicked.connect(self.elevator_1f_call)
        self.pushButton_2f.clicked.connect(self.elevator_2f_call)
        self.pushButton_3f.clicked.connect(self.elevator_3f_call)
        self.pushButton_e.clicked.connect(self.entrance_open)

        self.pushButton_air.clicked.connect(self.control_air)
        self.pushButton_heat.clicked.connect(self.control_heat)
        self.pushButton_humi.clicked.connect(self.control_hum)

        self.pushButton_curOpen.clicked.connect(self.curtain_open)
        self.pushButton_curClose.clicked.connect(self.curtain_close)
        self.pushButton_curStop.clicked.connect(self.curtain_stop)
        self.pushButton_curAuto.clicked.connect(self.curtain_auto)
        
        # Initially hide all check icons
        self.label_ele_1f.setText("")
        self.label_ele_2f.setText("")
        self.label_ele_3f.setText("")

        self.air_state = 0
        self.heat_state = 0
        self.hum_state = 0
        self.curtain_auto_mode = False

    def init_serial_ports(self):
        for name, port in SERIAL_PORTS.items():
            thread = SerialThread(serial_port=port, baud_rate=9600)
            thread.received_data.connect(self.handle_serial_data)
            thread.start()
            self.serial_threads[name] = thread
            print(f"Started serial thread for {name} on {port}")

    def entrance_open(self):
        command = "CMO,MOTOR,1\n"
        if 'ent_00' in self.serial_threads:
            self.serial_threads['ent_00'].write(command)
            self.label_e_approv.setText("✅")

    def elevator_1f_call(self):
        command = "CMO,FLOOR,1\n"
        if 'ele_00' in self.serial_threads:
            self.serial_threads['ele_00'].write(command)
            self.label_ele_1f.setText("✅")

    def elevator_2f_call(self):
        command = "CMO,FLOOR,2\n"
        if 'ele_00' in self.serial_threads:
            self.serial_threads['ele_00'].write(command)
            self.label_ele_2f.setText("✅")

    def elevator_3f_call(self):
        command = "CMO,FLOOR,3\n"
        if 'ele_00' in self.serial_threads:
            self.serial_threads['ele_00'].write(command)
            self.label_ele_3f.setText("✅")

    def control_air(self):
        if 'dht_00' not in self.serial_threads:
            return
        if self.air_state == 0:
            command = "A"
            self.label_airState.setText("ON")
            self.air_state = 1
        elif self.air_state == 1:
            command = "B"
            self.label_airState.setText("AUTO")
            self.air_state = 2
        else:
            command = "G"
            self.label_airState.setText("OFF")
            self.air_state = 0
        self.serial_threads['dht_00'].write(command)

    def control_heat(self):
        if 'dht_00' not in self.serial_threads:
            return
        if self.heat_state == 0:
            command = "C"
            self.label_heatState.setText("ON")
            self.heat_state = 1
        elif self.heat_state == 1:
            command = "D"
            self.label_heatState.setText("AUTO")
            self.heat_state = 2
        else:
            command = "H"
            self.label_heatState.setText("OFF")
            self.heat_state = 0
        self.serial_threads['dht_00'].write(command)

    def control_hum(self):
        if 'dht_00' not in self.serial_threads:
            return
        if self.hum_state == 0:
            command = "E"
            self.label_humiState.setText("ON")
            self.hum_state = 1
        elif self.hum_state == 1:
            command = "F"
            self.label_humiState.setText("AUTO")
            self.hum_state = 2
        else:
            command = "I"
            self.label_humiState.setText("OFF")
            self.hum_state = 0
        self.serial_threads['dht_00'].write(command)

    def curtain_open(self):
        command = "CMO,MOTOR,OPEN\n"
        if 'cur_00' in self.serial_threads:
            self.serial_threads['cur_00'].write(command)

    def curtain_close(self):
        command = "CMO,MOTOR,CLOSE\n"
        if 'cur_00' in self.serial_threads:
            self.serial_threads['cur_00'].write(command)

    def curtain_stop(self):
        command = "CMO,MOTOR,STOP\n"
        if 'cur_00' in self.serial_threads:
            self.serial_threads['cur_00'].write(command)

    def curtain_auto(self):
        self.curtain_auto_mode = not self.curtain_auto_mode
        mode = "1" if self.curtain_auto_mode else "0"
        command = f"CMO,MODE,AUTO,{mode}\n"
        if 'cur_00' in self.serial_threads:
            self.serial_threads['cur_00'].write(command)

    def handle_serial_data(self, port, data):
        device_name = None
        for name, p in SERIAL_PORTS.items():
            if p == port:
                device_name = name
                break
        
        if not device_name:
            print(f"Data from unknown port {port}: {data}")
            return

        if device_name == 'ele_00':
            if data == "ACK,FLOOR,1":
                self.label_ele_1f.setText("")
            elif data == "ACK,FLOOR,2":
                self.label_ele_2f.setText("")
            elif data == "ACK,FLOOR,3":
                self.label_ele_3f.setText("")
            elif data.startswith("SEN,FLOOR,"):
                try:
                    floor_number = int(data.split(',')[2])
                    self.lcdNumber_floor.display(floor_number)
                except (ValueError, IndexError) as e:
                    print(f"Error parsing elevator floor number from data '{data}': {e}")
        
        elif device_name == 'ent_00':
            parts = data.split(',')
            if len(parts) != 3:
                print(f"[ERROR] invalid entrance data: {data!r}")
                return
            
            data_type, metric_name, value = parts
            if data_type == "SEN":
                if metric_name == "RFID_ACCESS":
                    self.le_e_id.setText(str(value))
                    self.label_e_approv.setText("✅")
                elif metric_name == "RFID_DENY":
                    self.le_e_id.setText(str(value))
                    self.label_e_approv.setText("❌")
                elif metric_name == "MOTOR" and value == "-1":
                    self.le_e_id.clear()
                    self.label_e_approv.setText("")
        
        elif device_name == 'dht_00':
            try:
                if "SEN,TEM" in data and "HUM" in data:
                    parts = data.split(',')
                    temperature = float(parts[2])
                    humidity = int(parts[4])
                    
                    self.lcdNumber_temp.display(temperature)
                    self.lcdNumber_hu.display(humidity)
                    
                    self.graph_canvas.update_graph(temperature, humidity)
            except Exception as e:
                print(f"Error in dht_00 data handling from data '{data}': {e}")
        
        elif device_name == 'cur_00':
            parts = data.split(',')
            if len(parts) < 2:
                print(f"[ERROR] invalid curtain data: {data!r}")
                return
            
            data_type = parts[0]
            metric_name = parts[1]

            if data_type == 'SEN':
                try:
                    value = parts[2]
                    if metric_name == 'CUR_STEP':
                        self.progressBar_cur.setValue(int(value))
                    elif metric_name == 'LIGHT':
                        self.lcdNumber_lux.display(int(value))
                except (ValueError, IndexError) as e:
                    print(f"Error parsing curtain sensor data '{data}': {e}")
            elif data_type == 'ACK':
                if len(parts) < 3:
                    print(f"[ERROR] invalid curtain ack: {data!r}")
                    return
                value = parts[2]
                if metric_name == 'MOTOR':
                    state = "OPEN" if value == "1" else "CLOSE" if value == "2" else "STOP"
                    self.label_curState.setText(f"AUTO {state}")
                elif metric_name == 'STATE':
                    self.label_curState.setText(value) # e.g., OPEN, CLOSE, STOP


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    sys.exit(app.exec())
