import cv2
import numpy as np
import urllib.request
import threading
import time


class ESP32Camera:
    # ip lấy từ esp32 cam 
    def __init__(self, ip="192.168.137.6"):
        self.ip = ip
        self.stream_url = f"http://{self.ip}:81/stream"

        self.latest_frame = None
        self.running = False
        self.thread = None

    def connect(self):
        while self.running:
            try:
                print("Connecting to camera stream...")
                return urllib.request.urlopen(self.stream_url, timeout=10)
            except:
                print("Camera connection failed. Retrying...")
                time.sleep(2)

        return None

    def reader(self):
        buffer = b""

        while self.running:
            stream = self.connect()

            if stream is None:
                continue

            try:
                while self.running:
                    chunk = stream.read(8192)
                    if not chunk:
                        continue

                    buffer += chunk

                    if len(buffer) > 200000:
                        buffer = buffer[-100000:]

                    start = buffer.find(b'\xff\xd8')
                    end = buffer.find(b'\xff\xd9', start + 2)

                    if start != -1 and end != -1:
                        jpg = buffer[start:end + 2]
                        buffer = buffer[end + 2:]

                        frame = cv2.imdecode(
                            np.frombuffer(jpg, dtype=np.uint8),
                            cv2.IMREAD_COLOR
                        )

                        if frame is not None:
                            self.latest_frame = frame

            except:
                print("Camera stream lost. Reconnecting...")
                time.sleep(1)

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.reader, daemon=True)
        self.thread.start()
        print("Camera reader started")

    def get_frame(self):
        if self.latest_frame is not None:
            return self.latest_frame.copy()
        return None

    def stop(self):
        self.running = False
        print("Camera stopped")
