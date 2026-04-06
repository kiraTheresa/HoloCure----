import cv2
import mss
import numpy as np

with mss.mss() as sct:
    monitor = sct.monitors[1]
    print(f"Capturing: {monitor['width']}x{monitor['height']} @ ({monitor['left']}, {monitor['top']})")

    while True:
        img = np.array(sct.grab(monitor))
        frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        cv2.imshow("Screen Capture", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cv2.destroyAllWindows()
