import cv2
import mss
import numpy as np
import win32gui
import win32api
import win32con
import time
import os

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates", "1920_1080", "opaque")
TEMPLATE_NAMES = ["up_54_63", "down_54_63", "left_60_57", "right_60_57", "circle_48_51"]
MATCH_THRESHOLD = 0.7

TRIGGER_ZONE = {
    "x1": 1120,
    "y1": 720,
    "x2": 1230,
    "y2": 830
}

TEMPLATE_TO_KEY = {
    "up_54_63": "W",
    "down_54_63": "S",
    "left_60_57": "A",
    "right_60_57": "D",
    "circle_48_51": "SPACE"
}

KEY_CODE = {
    "W": 0x57,
    "A": 0x41,
    "S": 0x53,
    "D": 0x44,
    "SPACE": 0x20
}


def imread_unicode(path, flags=cv2.IMREAD_COLOR):
    data = np.fromfile(path, dtype=np.uint8)
    img = cv2.imdecode(data, flags)
    return img


def load_templates():
    templates = {}
    for name in TEMPLATE_NAMES:
        path = os.path.join(TEMPLATE_DIR, f"{name}.png")
        if os.path.exists(path):
            tpl = imread_unicode(path, cv2.IMREAD_GRAYSCALE)
            if tpl is not None:
                templates[name] = tpl
                print(f"已加载模板: {name}")
    return templates


def find_window(title):
    hwnd = win32gui.FindWindow(None, title)
    return hwnd if hwnd != 0 else None


def get_client_rect(hwnd):
    client_rect = win32gui.GetClientRect(hwnd)
    client_left_top = win32gui.ClientToScreen(hwnd, (0, 0))
    return client_left_top[0], client_left_top[1], client_rect[2], client_rect[3]


def press_key(key_name):
    vk_code = KEY_CODE.get(key_name)
    if vk_code:
        win32api.keybd_event(vk_code, 0, 0, 0)
        time.sleep(0.05)
        win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)
        print(f"[触发] {key_name}")


def match_best(roi_gray, templates):
    best_score = 0
    best_name = None
    best_loc = None

    for name, tpl in templates.items():
        result = cv2.matchTemplate(roi_gray, tpl, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        if max_val > best_score:
            best_score = max_val
            best_name = name
            best_loc = max_loc

    return best_name, best_score, best_loc


def main():
    target_title = "HoloCure"

    x1, y1 = TRIGGER_ZONE["x1"], TRIGGER_ZONE["y1"]
    x2, y2 = TRIGGER_ZONE["x2"], TRIGGER_ZONE["y2"]
    zone_w, zone_h = x2 - x1, y2 - y1

    print(f"触发区域: ({x1},{y1}) -> ({x2},{y2}), 尺寸: {zone_w}x{zone_h}")

    templates = load_templates()
    if not templates:
        print("未加载到任何模板，退出")
        return

    hwnd = find_window(target_title)
    if hwnd is None:
        print(f"窗口 '{target_title}' 未找到")
        return

    print(f"已找到窗口: {target_title}")
    print("钓鱼脚本已启动，按 q 退出")

    last_press_time = 0
    press_cooldown = 0.15
    last_detect_time = time.time()
    no_detect_timeout = 5.0

    with mss.mss() as sct:
        prev_time = time.time()

        while True:
            left, top, width, height = get_client_rect(hwnd)

            monitor = {"left": left, "top": top, "width": width, "height": height}
            img = np.array(sct.grab(monitor))
            frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

            zone_frame = frame[y1:y2, x1:x2]
            zone_gray = cv2.cvtColor(zone_frame, cv2.COLOR_BGR2GRAY)

            name, score, loc = match_best(zone_gray, templates)

            curr_time = time.time()
            triggered = False

            if score >= MATCH_THRESHOLD:
                last_detect_time = curr_time

                key_name = TEMPLATE_TO_KEY.get(name)
                if key_name and curr_time - last_press_time > press_cooldown:
                    press_key(key_name)
                    last_press_time = curr_time
                    triggered = True

                tpl_h, tpl_w = templates[name].shape[:2]
                cv2.rectangle(zone_frame, loc, (loc[0] + tpl_w, loc[1] + tpl_h), (0, 255, 0), 2)
                cv2.putText(zone_frame, f"{name.split('_')[0]} ({score:.2f})",
                            (loc[0], loc[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

            if curr_time - last_detect_time > no_detect_timeout:
                print(f"[超时] {no_detect_timeout}秒未检测到符号，执行两次空格")
                press_key("SPACE")
                time.sleep(0.2)
                press_key("SPACE")
                last_detect_time = curr_time

            fps = 1 / (curr_time - prev_time)
            prev_time = curr_time

            cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 0), 2)
            cv2.imshow("Trigger Zone", zone_frame)
            cv2.imshow("Full Screen", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
