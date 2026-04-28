import cv2
import math
from deep_sort_realtime.deepsort_tracker import DeepSort


class PersonTracker:
    def __init__(self, max_age=30):
        self.tracker = DeepSort(max_age=max_age)
        self.target_id = None

    def update(self, detections, frame):
        """
        detections từ YOLO:
        [
            {
                "bbox": (x, y, w, h),
                "conf": confidence
            }
        ]
        """

        ds_detections = []

        for det in detections:
            x, y, w, h = det["bbox"]
            conf = det["conf"]

            ds_detections.append(([x, y, w, h], conf, 'person'))

        tracks = self.tracker.update_tracks(ds_detections, frame=frame)

        valid_tracks = []

        for track in tracks:
            if not track.is_confirmed():
                continue

            track_id = track.track_id
            x1, y1, x2, y2 = map(int, track.to_ltrb())

            w = x2 - x1
            h = y2 - y1

            cx = x1 + w // 2
            cy = y1 + h // 2

            valid_tracks.append({
                "id": track_id,
                "bbox": (x1, y1, w, h),
                "center": (cx, cy)
            })

        return valid_tracks

    def select_target(self, tracks, center_x, center_y):
        """
        chọn target để điều khiển camera
        """

        if len(tracks) == 0:
            self.target_id = None
            return None

        # nếu chưa có target → chọn gần center nhất
        if self.target_id is None:
            target = min(
                tracks,
                key=lambda t: (t["center"][0] - center_x)**2 +
                              (t["center"][1] - center_y)**2
            )
            self.target_id = target["id"]
            return target

        # nếu đã có target → tìm lại theo ID
        for t in tracks:
            if t["id"] == self.target_id:
                return t

        # nếu mất target → reset
        self.target_id = None
        return None

    def draw(self, frame, tracks, target=None):
        """
        vẽ bbox + ID + highlight target
        """

        for t in tracks:
            x, y, w, h = t["bbox"]
            cx, cy = t["center"]
            tid = t["id"]

            color = (0, 255, 0)

            if target is not None and tid == target["id"]:
                color = (0, 0, 255)  # target màu đỏ

            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            cv2.putText(frame, f"ID {tid}",
                        (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, color, 2)

            cv2.circle(frame, (cx, cy), 5, color, -1)

        return frame