import sys
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6 import uic
from PyQt6.QtCore import *
import serial

# Receiver는 시리얼 데이터를 읽어오는 백그라운드 스레드입니다.
class Receiver(QThread):
    # 시리얼 데이터를 메인 스레드로 전달할 신호
    SerialMonitor = pyqtSignal(str)

    def __init__(self, conn, parent=None):
        super(Receiver, self).__init__(parent)
        self.is_running = True  # 수신 중인지 여부
        self.conn = conn
        print("Receiver initialized")

    def run(self):
        # 수신을 시작
        while self.is_running:
            if self.conn.in_waiting > 0:  # 읽을 데이터가 있으면
                data = self.conn.readline()
                try:
                    # 데이터를 utf-8로 디코딩하고, 오류가 나면 무시하도록 설정
                    data = data.decode('utf-8', errors='ignore').strip()  # 오류가 나면 무시
                except UnicodeDecodeError:
                    print("Decoding error occurred, skipping line.")
                    continue  # 오류가 발생하면 해당 라인은 무시하고 계속 진행
                if data:
                    self.SerialMonitor.emit(data)  # 시리얼 데이터를 메인 스레드로 전달


# UI를 로드하고 기본 윈도우 클래스를 설정합니다.
from_class = uic.loadUiType("project.ui")[0]

class WindowClass(QMainWindow, from_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # 시리얼 포트와 연결
        self.conn = serial.Serial(port='/dev/ttyACM0', baudrate=9600, timeout=1)

        # Receiver 객체 생성 및 시작
        self.recv = Receiver(self.conn)
        self.recv.start()

        # 시리얼 데이터가 오면 SerialMonitor 슬롯을 호출하도록 연결
        self.recv.SerialMonitor.connect(self.SerialMonitor)

        #기본기능
        self.pbnAir.clicked.connect(self.Air_on)
        self.pbnHeat.clicked.connect(self.Heat_on)
        self.pbnHum.clicked.connect(self.Hum_on)
        self.pbnAir_2.clicked.connect(self.Air_off)
        self.pbnHeat_2.clicked.connect(self.Heat_off)
        self.pbnHum_2.clicked.connect(self.Hum_off)
        self.pbnAuto.clicked.connect(self.Auto)

    def SerialMonitor(self, data):
        # 시리얼 데이터를 textBrowser에 추가
        self.textBrowser.append(data)

    def closeEvent(self, event):
        # 창을 닫을 때, Receiver 스레드를 종료
        self.recv.is_running = False
        self.recv.wait()  # 스레드가 종료될 때까지 기다림

    def Air_on (self):
        self.lineEdit.setText("에어컨 가동")
        if self.conn.is_open:
            self.conn.write(b'A') 
    def Air_off(self):
        self.lineEdit.setText("에어컨 종료")
        if self.conn.is_open:
            self.conn.write(b'B')  # 필요시 다른 명령을 전송하여 모터 종료
    def Heat_on (self):
        self.lineEdit.setText("히터 가동")
        if self.conn.is_open:
            self.conn.write(b'C') 
    def Heat_off (self):
        self.lineEdit.setText("히터 종료")
        if self.conn.is_open:
            self.conn.write(b'D') 

    def Hum_on (self):
        self.lineEdit.setText("가습기 가동")
        if self.conn.is_open:
            self.conn.write(b'E') 
    def Hum_off (self):
        self.lineEdit.setText("가습기 종료")
        if self.conn.is_open:
            self.conn.write(b'F') 

    def Auto (self):
        self.lineEdit.setText("자동모드 가동")
        if self.conn.is_open:
            self.conn.write(b'G') 


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindows = WindowClass()
    myWindows.show()

    sys.exit(app.exec())
