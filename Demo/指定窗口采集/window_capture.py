import cv2
import mss
import numpy as np
import win32gui
import time


def find_window(title):
    hwnd = win32gui.FindWindow(None, title)
    if hwnd == 0:
        return None
    return hwnd


def get_window_rect(hwnd):
    return win32gui.GetWindowRect(hwnd)


def main():
    target_title = "HoloCure"

    hwnd = find_window(target_title)
    if hwnd is None:
        print(f"窗口 '{target_title}' 未找到，请确认窗口已打开")
        return

    print(f"已找到窗口: {target_title} (hwnd={hwnd})")

    with mss.mss() as sct:
        prev_time = time.time()
        fps = 0

        while True:
            left, top, right, bottom = get_window_rect(hwnd)
            width = right - left
            height = bottom - top

            monitor = {
                "left": left,
                "top": top,
                "width": width,
                "height": height
            }

            print(f"窗口坐标: left={left}, top={top}, width={width}, height={height}")

            img = np.array(sct.grab(monitor))
            frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

            curr_time = time.time()
            fps = 1 / (curr_time - prev_time)
            prev_time = curr_time

            cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow("Window Capture", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
