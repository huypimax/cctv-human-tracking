import cv2
import time
from camera import ESP32Camera
from detection import PersonDetector
from tracking import PersonTracker
from serial_communication import SerialCommunication


ESP32_IP = "192.168.137.8"
SERIAL_PORT = "COM4"
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
CENTER_X = FRAME_WIDTH // 2
CENTER_Y = FRAME_HEIGHT // 2
Kp = 0.02
DEAD_ZONE = 20
CONTROL_INTERVAL = 0.1

cam = ESP32Camera(ESP32_IP)
detector = PersonDetector()
tracker = PersonTracker()
ser = SerialCommunication(SERIAL_PORT)

cam.start()
print("System started...")

next_control = time.perf_counter()

while True:
    frame = cam.get_frame()
    if frame is None:
        continue

    frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))
    detections = detector.detect(frame)
    tracks = tracker.update(detections, frame)
    target = tracker.select_target(tracks, CENTER_X, CENTER_Y)

    now = time.perf_counter()

    if target is not None:
        cx, cy = target["center"]

        error_x = CENTER_X - cx
        error_y = CENTER_Y - cy

        # dead zone
        if abs(error_x) < DEAD_ZONE:
            error_x = 0
        if abs(error_y) < DEAD_ZONE:
            error_y = 0

        if now >= next_control:
            next_control += CONTROL_INTERVAL

            ux = Kp * error_x
            uy = Kp * error_y

            ser.send_control(ux, uy)

        # debug
        cv2.circle(frame, (cx, cy), 6, (0, 0, 255), -1)
        cv2.line(frame, (CENTER_X, CENTER_Y), (cx, cy), (255, 0, 0), 2)

    else:
        cv2.putText(frame, "NO TARGET",
                    (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1, (0, 0, 255), 2)

    frame = tracker.draw(frame, tracks, target)
    cv2.circle(frame, (CENTER_X, CENTER_Y), 5, (255, 0, 0), -1)
    cv2.imshow("CCTV Human Tracking", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cam.stop()
ser.close()
cv2.destroyAllWindows()