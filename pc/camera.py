import cv2
import numpy as np
import urllib.request
import threading
import time


class ESP32Camera:
    def __init__(self, ip):
        self.stream_url = f"http://{ip}:81/stream"
        self.latest_frame = None
        self.running = False
        self.thread = None

    def _connect(self):
        while True:
            try:
                print("Connecting to:", self.stream_url)
                stream = urllib.request.urlopen(self.stream_url, timeout=10)
                print("Connected to ESP32-CAM")
                return stream
            except Exception as e:
                print("Connection failed:", e)
                time.sleep(2)

    def _reader(self):
        buffer = b""

        while self.running:
            stream = self._connect()
            buffer = b""

            try:
                while self.running:
                    chunk = stream.read(8192)
                    if not chunk:
                        continue

                    buffer += chunk

                    # tránh buffer quá lớn
                    if len(buffer) > 200000:
                        buffer = buffer[-100000:]

                    while True:
                        start = buffer.find(b'\xff\xd8')
                        end = buffer.find(b'\xff\xd9', start + 2)

                        if start == -1 or end == -1:
                            break

                        jpg = buffer[start:end + 2]
                        buffer = buffer[end + 2:]

                        frame = cv2.imdecode(
                            np.frombuffer(jpg, dtype=np.uint8),
                            cv2.IMREAD_COLOR
                        )

                        if frame is not None:
                            self.latest_frame = frame

            except Exception as e:
                print("Stream lost:", e)
                time.sleep(1)

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._reader, daemon=True)
            self.thread.start()

    def stop(self):
        self.running = False

    def get_frame(self):
        return self.latest_frame