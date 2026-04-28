import cv2
from ultralytics import YOLO


class PersonDetector:
    def __init__(self, model_path="yolov8n.pt", conf_threshold=0.5):
        """
        model_path: đường dẫn model YOLO
        conf_threshold: ngưỡng confidence
        """
        self.model = YOLO(model_path)
        self.conf_threshold = conf_threshold

    def detect(self, frame):
        """
        Input:
            frame (BGR image)

        Output:
            detections: list dict
            [
                {
                    "bbox": (x, y, w, h),
                    "center": (cx, cy),
                    "conf": confidence
                }
            ]
        """
        results = self.model(frame, verbose=False)[0]

        detections = []

        for box in results.boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])

            # class 0 = person (COCO)
            if cls_id == 0 and conf > self.conf_threshold:
                x1, y1, x2, y2 = map(int, box.xyxy[0])

                w = x2 - x1
                h = y2 - y1

                cx = x1 + w // 2
                cy = y1 + h // 2

                detections.append({
                    "bbox": (x1, y1, w, h),
                    "center": (cx, cy),
                    "conf": conf
                })

        return detections

    def draw(self, frame, detections):
        """
        Vẽ bounding box + center lên frame
        """
        for det in detections:
            x, y, w, h = det["bbox"]
            cx, cy = det["center"]
            conf = det["conf"]

            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)

            cv2.putText(frame, f"{conf:.2f}",
                        (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (0, 255, 0), 2)

        return frame