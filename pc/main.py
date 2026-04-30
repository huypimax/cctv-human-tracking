import cv2
import time

from camera import ESP32Camera
from detection import PersonDetector
from tracking import PersonTracker
from serial_communication import SerialCommunication
from control import FaceTrackerController


# =========================
# Configuration
# =========================
ESP32_IP = "192.168.137.8"
SERIAL_PORT = "COM4"
BAUDRATE = 115200

FRAME_WIDTH = 640
FRAME_HEIGHT = 480

CENTER_X = FRAME_WIDTH // 2
CENTER_Y = FRAME_HEIGHT // 2

Kp = 0.02
DEAD_ZONE = 20
CONTROL_INTERVAL = 0.1

HOME_PAN = 90
HOME_TILT = 40
NO_TARGET_HOME_TIME = 3.0


# =========================
# Init modules
# =========================
cam = ESP32Camera(ESP32_IP)
detector = PersonDetector()
tracker = PersonTracker()

ser = SerialCommunication(
    port=SERIAL_PORT,
    baudrate=BAUDRATE,
    timeout=1
)

controller = FaceTrackerController(
    cx=CENTER_X,
    cy=CENTER_Y,
    kp_pan=Kp,
    kp_tilt=Kp,
    dead_zone=DEAD_ZONE
)


# =========================
# Start system
# =========================
ser.connect()
cam.start()

print("System started...")

next_control = time.perf_counter()
last_seen_time = time.perf_counter()
returned_home = False


# =========================
# Main loop
# =========================
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
        target_x, target_y = target["center"]

        last_seen_time = now
        returned_home = False

        # Control every CONTROL_INTERVAL seconds
        if now >= next_control:
            next_control += CONTROL_INTERVAL

            ux, uy, error_x, error_y = controller.compute_control(
                target_x,
                target_y
            )

            ser.send_control(ux, uy)

            print(
                "error_x =", error_x,
                "error_y =", error_y,
                "ux =", round(ux, 2),
                "uy =", round(uy, 2)
            )

        # Debug target position
        cv2.circle(frame, (target_x, target_y), 6, (0, 0, 255), -1)
        cv2.line(
            frame,
            (CENTER_X, CENTER_Y),
            (target_x, target_y),
            (255, 0, 0),
            2
        )

        cv2.putText(
            frame,
            "TARGET LOCKED",
            (50, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

    else:
        cv2.putText(
            frame,
            "NO TARGET",
            (50, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 255),
            2
        )

        # If no target for 3 seconds, return servo to home once
        if (now - last_seen_time >= NO_TARGET_HOME_TIME) and (not returned_home):
            ser.send_home(HOME_PAN, HOME_TILT)
            print("No target 3s -> HOME")
            returned_home = True

    # Draw tracker result
    frame = tracker.draw(frame, tracks, target)

    # Draw image center
    cv2.circle(frame, (CENTER_X, CENTER_Y), 5, (255, 0, 0), -1)

    cv2.imshow("CCTV Human Tracking", frame)

    # Press ESC to exit
    if cv2.waitKey(1) & 0xFF == 27:
        break


# =========================
# Cleanup
# =========================
cam.stop()
ser.close()
cv2.destroyAllWindows()