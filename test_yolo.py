from ultralytics import YOLO
import cv2
import numpy as np

model = YOLO("yolo11n-pose.pt")
# Create a dummy image
img = np.zeros((480, 640, 3), dtype=np.uint8)
# Add some fake data
cv2.circle(img, (320, 240), 50, (255, 255, 255), -1)

results = model(img)
for r in results:
    if r.keypoints is not None:
        kp_data = r.keypoints.xy.cpu().numpy()
        print("Keypoints structure:")
        print(kp_data)
        for kp in kp_data:
            print("Processing person kp:", kp)
            if len(kp) < 5:
                print("Too few points")
                continue
            face_pts = kp[0:5]
            valid_pts = [p for p in face_pts if p[0] > 0 and p[1] > 0]
            print("Valid points:", valid_pts)
            if len(valid_pts) < 3:
                print("Skipping due to <3 valid points")
                continue
