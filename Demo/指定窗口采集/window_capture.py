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


def get_client_rect(hwnd):
    client_rect = win32gui.GetClientRect(hwnd)
    client_width = client_rect[2]
    client_height = client_rect[3]

    client_left_top = win32gui.ClientToScreen(hwnd, (0, 0))
    client_left = client_left_top[0]
    client_top = client_left_top[1]

    return client_left, client_top, client_width, client_height


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
            left, top, width, height = get_client_rect(hwnd)

            monitor = {
                "left": left,
                "top": top,
                "width": width,
                "height": height
            }

            print(f"客户区坐标: left={left}, top={top}, width={width}, height={height}")

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
