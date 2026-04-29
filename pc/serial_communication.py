import serial
import time


class SerialCommunication:
    #tùy vào esp32 kết nối cổng COM nào
    def __init__(self, port="COM4", baudrate=115200):
        try:
            self.ser = serial.Serial(port, baudrate, timeout=1)
            time.sleep(2)  # đợi ESP32 reset
            print(f"Connected to {port}")
        except Exception as e:
            print("Serial connection failed:", e)
            self.ser = None

    def send_control(self, ux, uy):
        if self.ser:
            cmd = f"CTRL,{ux:.2f},{uy:.2f}\n"
            self.ser.write(cmd.encode())

    def send_home(self, pan=90, tilt=40):
        if self.ser:
            cmd = f"HOME,{pan},{tilt}\n"
            self.ser.write(cmd.encode())

    def close(self):
        if self.ser:
            self.ser.close()
            print("Serial closed")