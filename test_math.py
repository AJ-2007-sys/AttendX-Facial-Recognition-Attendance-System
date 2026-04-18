import numpy as np
import cv2

frame = np.zeros((480, 640, 3), dtype=np.uint8)

# Simulate keypoints: Nose(320, 240), LEye(300, 220), REye(340, 220), LEar(280, 230), REar(360, 230)
face_pts = np.array([
    [320, 240],
    [300, 220],
    [340, 220],
    [280, 230],
    [360, 230]
])

xs = face_pts[:, 0]
ys = face_pts[:, 1]

x_min, y_min = np.min(xs), np.min(ys)
x_max, y_max = np.max(xs), np.max(ys)

head_width = x_max - x_min
head_height = head_width * 1.5

center_x = np.mean(xs)
center_y = np.mean(ys) + (head_height * 0.1)

x1 = int(max(0, center_x - head_width * 0.7))
x2 = int(min(frame.shape[1], center_x + head_width * 0.7))
y1 = int(max(0, center_y - head_height * 0.5))
y2 = int(min(frame.shape[0], center_y + head_height * 0.6))

print(f"Bbox: ({x1}, {y1}) to ({x2}, {y2}), size: {x2-x1}x{y2-y1}")
# Eye to nose vertical was 240-220 = 20
# Ear to ear width is 360-280 = 80
# Box size should be around 80*1.4 = 112 wide, 120 tall.
