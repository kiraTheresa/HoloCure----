# HoloCure 钓鱼 QTE 自动化 —— 技术栈与实现规范（Python + OpenCV）

## 1. 项目目标

实现一个基于视觉识别的自动化程序，用于完成 HoloCure 钓鱼小游戏中的 QTE（Quick Time Event）输入。

核心能力：

* 实时屏幕采集
* QTE符号识别（↑ ↓ ← → ○）
* 判定时机控制
* 自动按键输入
* 循环执行钓鱼流程

---

## 2. 技术栈选型

### 2.1 语言

* Python 3.10+

---

### 2.2 核心依赖

```bash
pip install mss opencv-python numpy pynput
```

---

### 2.3 各模块技术说明

#### 屏幕采集

* 库：mss
* 用途：高性能屏幕截图（替代 pyautogui）
* 要求：≥10 FPS

---

#### 图像处理

* 库：opencv-python (cv2)
* 用途：
  * ROI裁剪
  * 模板匹配（cv2.matchTemplate）
  * 可视化调试（cv2.imshow）

---

#### 数值计算

* 库：numpy
* 用途：图像数据处理

---

#### 输入控制

* 库：pynput
* 用途：键盘模拟（比 pyautogui 更稳定）

---

## 3. 系统架构

```text
main loop:
    capture frame
    crop ROI
    detect symbols
    evaluate trigger
    send key input
```

模块划分：

```text
project/
├── main.py
├── capture.py
├── vision.py
├── controller.py
├── input.py
├── config.py
└── templates/
```

---

## 4. 核心模块设计

---

### 4.1 capture.py（屏幕采集）

功能：

* 获取屏幕帧
* 返回 numpy array（BGR）

要求：

* 使用 mss
* 不做额外处理

---

### 4.2 vision.py（视觉识别）

功能：

* 裁剪 ROI（QTE区域）
* 模板匹配识别符号

#### 输入：

* frame（整屏图像）

#### 输出：

```python
[
    {"type": "left", "x": 123, "y": 456},
    {"type": "circle", "x": 200, "y": 460}
]
```

---

#### 模板要求：

路径：

```text
templates/
  up.png
  down.png
  left.png
  right.png
  circle.png
```

要求：

* 尺寸固定
* 与游戏UI一致
* 使用彩色图（不要灰度模板）

---

#### 匹配方法：

```python
cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
```

阈值建议：

```python
threshold = 0.7 ~ 0.85
```

---

### 4.3 controller.py（决策逻辑）

功能：

* 判断符号是否进入判定区
* 控制是否触发按键

---

#### 判定规则：

定义：

```python
TRIGGER_X = 固定值（判定线）
TOLERANCE = 误差范围（如 ±10px）
```

触发条件：

```python
abs(symbol_x - TRIGGER_X) < TOLERANCE
```

---

#### 去重机制（必须实现）：

```python
已触发符号不能重复触发
```

实现方式：

* 记录最近触发位置
* 或为每个符号打标记

---

---

### 4.4 input.py（输入控制）

功能：

* 根据符号发送按键

映射：

```python
{
    "up": "w",
    "down": "s",
    "left": "a",
    "right": "d",
    "circle": "space"
}
```

---

#### 要求：

* 使用 pynput.keyboard.Controller
* 每次按键：
  * press
  * 短延迟（10~30ms）
  * release

---

#### 节流：

```python
按键间隔 ≥ 50ms
```

---

### 4.5 main.py（主循环）

逻辑：

```python
while True:
    frame = capture()

    roi = crop(frame)

    symbols = detect(roi)

    for symbol in symbols:
        if should_trigger(symbol):
            press_key(symbol)
```

---

## 5. ROI（关键优化）

必须裁剪：

```python
roi = frame[y1:y2, x1:x2]
```

区域：

* QTE滑动条区域（中间水平区域）

目的：

* 提高性能
* 减少误识别

---

## 6. Debug机制（必须实现）

实时显示：

```python
cv2.imshow("debug", roi)
```

显示内容：

* 检测框
* 判定线
* 符号位置

---

## 7. 性能要求

| 指标       | 目标    |
| ---------- | ------- |
| FPS        | ≥ 10   |
| 延迟       | < 100ms |
| 识别准确率 | > 95%   |

---

## 8. 开发阶段建议

### Phase 1

* 屏幕采集 + ROI显示

### Phase 2

* 单个符号识别（模板匹配）

### Phase 3

* 多符号检测

### Phase 4

* 判定触发

### Phase 5

* 输入控制

---

## 9. 关键约束

必须满足：

* 游戏窗口分辨率固定（推荐 1920x1080）
* 游戏窗口位置固定
* UI不可缩放

---

## 10. 非目标（暂不实现）

* 不做深度学习
* 不做自适应分辨率
* 不做跨版本兼容

---

## 11. 扩展方向（可选）

* 感叹号检测（进入QTE判定）
* 成功/失败识别
* 自动循环钓鱼
* 多线程优化

---

## 12. 成功标准

系统能够：

* 连续完成钓鱼QTE
* 成功率 ≥ 90%
* 无明显卡顿或误触

---

END
