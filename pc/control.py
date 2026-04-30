class FaceTrackerController:
    def __init__(
        self,
        cx=320,
        cy=240,
        kp_pan=0.02,
        kp_tilt=0.02,
        dead_zone=20
    ):
        self.cx = cx
        self.cy = cy

        self.kp_pan = kp_pan
        self.kp_tilt = kp_tilt

        self.dead_zone = dead_zone

    def compute_control(self, fx, fy):
        """
        Tính tín hiệu điều khiển servo từ vị trí khuôn mặt.

        fx, fy: tọa độ tâm khuôn mặt
        cx, cy: tọa độ tâm ảnh

        ex = cx - fx
        ey = cy - fy

        ux: lệnh điều khiển servo pan
        uy: lệnh điều khiển servo tilt
        """

        ex = self.cx - fx
        ey = self.cy - fy

        ux = self.kp_pan * ex
        uy = self.kp_tilt * ey

        # Vùng chết: nếu sai số nhỏ thì không điều khiển
        # để tránh servo rung liên tục
        if abs(ex) < self.dead_zone:
            ux = 0

        if abs(ey) < self.dead_zone:
            uy = 0

        return ux, uy, ex, ey