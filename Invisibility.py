import cv2
import numpy as np
import time

# Open webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ Could not access the camera. Try using index 1 or 2.")
    exit()

# Countdown for background capture
print("⏳ Capturing background in 3 seconds... Stay still!")
time.sleep(3)

# Capture the background
print("📸 Capturing background... please stay still")
for _ in range(60):
    ret, bg = cap.read()
    if ret:
        bg = cv2.flip(bg, 1)
print("✅ Background captured")

prev_time = 0  # For FPS calculation

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, (640, 480))
    frame = cv2.flip(frame, 1)  # Mirror view
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # --- Red color range (two ranges due to hue wrapping) ---
    lower_red1 = np.array([0, 120, 70])
    upper_red1 = np.array([10, 255, 255])

    lower_red2 = np.array([170, 120, 70])
    upper_red2 = np.array([180, 255, 255])

    # Create masks for red
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = mask1 + mask2

    # Refine mask
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8), iterations=2)
    mask = cv2.dilate(mask, np.ones((3, 3), np.uint8), iterations=1)
    mask = cv2.medianBlur(mask, 5)

    # Replace red cloak region with background
    cloak_area = cv2.bitwise_and(bg, bg, mask=mask)
    non_cloak_area = cv2.bitwise_and(frame, frame, mask=cv2.bitwise_not(mask))
    final = cv2.addWeighted(cloak_area, 1, non_cloak_area, 1, 0)

    # Smooth edges
    final = cv2.GaussianBlur(final, (5, 5), 0)

    # --- FPS counter ---
    curr_time = time.time()
    fps = 1 / (curr_time - prev_time) if prev_time != 0 else 0
    prev_time = curr_time
    cv2.putText(final, f'FPS: {int(fps)}', (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Show result
    cv2.imshow("🪄 Red Cloak Invisibility", final)

    # Controls
    key = cv2.waitKey(1) & 0xFF
    if key == 27:  # ESC to quit
        break
    elif key == ord('b'):  # Re-capture background
        print("♻️ Re-capturing background...")
        for _ in range(60):
            ret, bg = cap.read()
            if ret:
                bg = cv2.flip(bg, 1)
        print("✅ Background updated")

cap.release()
cv2.destroyAllWindows()
