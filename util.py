# -*- coding: utf-8 -*-
r'''
    ______  ______  _____________________  _________    __  ___
   / __ \ \/ / __ \/ ____/ ___/_  __/ __ \/ ____/   |  /  |/  /
  / /_/ /\  / /_/ / __/  \__ \ / / / /_/ / __/ / /| | / /|_/ /
 / ____/ / / ____/ /___ ___/ // / / _, _/ /___/ ___ |/ /  / /
/_/     /_/_/   /_____//____//_/ /_/ |_/_____/_/  |_/_/  /_/
action node script

'''

from __future__ import annotations

import dataclasses
import os
import subprocess
import time
from typing import Iterable

import base64
import cv2
import mss
import numpy as np
import pyautogui
import pytesseract
from PIL import Image, ImageChops, ImageStat


@dataclasses.dataclass
class OCRMatch:
    text: str
    bbox: tuple[int, int, int, int]
    confidence: float


def normalize_text(text: str) -> str:
    return "".join(ch.lower() for ch in text if ch.isalnum() or ch.isspace()).strip()


def take_screenshot() -> np.ndarray:
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        img = np.array(sct.grab(monitor))
        return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)


def save_screenshot(directory: str, name: str) -> str:
    os.makedirs(directory, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    path = os.path.join(directory, f"{name}_{ts}.png")
    img = take_screenshot()
    cv2.imwrite(path, img)
    return path


def find_text(targets: Iterable[str]) -> OCRMatch | None:
    img = take_screenshot()
    data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
    best_match = None
    targets_norm = [normalize_text(t) for t in targets]
    for i, text in enumerate(data["text"]):
        if not text.strip():
            continue
        norm = normalize_text(text)
        for target in targets_norm:
            if target and target in norm:
                conf = float(data["conf"][i])
                x = int(data["left"][i])
                y = int(data["top"][i])
                w = int(data["width"][i])
                h = int(data["height"][i])
                match = OCRMatch(text=text, bbox=(x, y, w, h), confidence=conf)
                if best_match is None or conf > best_match.confidence:
                    best_match = match
    return best_match


def click_text(match: OCRMatch, x_offset: int = 0, y_offset: int = 0) -> None:
    x, y, w, h = match.bbox
    click_x = x + w // 2 + x_offset
    click_y = y + h // 2 + y_offset
    pyautogui.click(click_x, click_y)


def click_xy(x: int, y: int) -> None:
    pyautogui.click(x, y)


def type_text(text: str) -> None:
    pyautogui.typewrite(text, interval=0.02)


def safe_sleep(seconds: float) -> None:
    time.sleep(seconds)


def press_key(key: str) -> None:
    pyautogui.press(key)


def open_chromium_with_url(url: str) -> None:
    app_candidates = [
        "/Applications/Chromium.app",
        "/Applications/Google Chrome.app",
    ]
    app = None
    for candidate in app_candidates:
        if os.path.exists(candidate):
            app = candidate
            break
    if app is None:
        raise RuntimeError("Chromium or Google Chrome not found in /Applications.")
    subprocess.Popen(
        ["open", "-a", app, "--args", "--new-window", url],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def get_screen_change_score() -> float:
    img1 = take_screenshot()
    time.sleep(0.5)
    img2 = take_screenshot()
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    diff = cv2.absdiff(gray1, gray2)
    score = float(np.mean(diff) / 255.0)
    return score


def image_to_base64_png(image: np.ndarray) -> str:
    success, buffer = cv2.imencode(".png", image)
    if not success:
        raise RuntimeError("Failed to encode image as PNG.")
    return base64.b64encode(buffer.tobytes()).decode("utf-8")


def bytes_to_base64_png(image_bytes: bytes) -> str:
    return base64.b64encode(image_bytes).decode("utf-8")


def image_bytes_change_score(img_bytes_a: bytes, img_bytes_b: bytes) -> float:
    img_a = Image.open(io_bytes(img_bytes_a)).convert("RGB")
    img_b = Image.open(io_bytes(img_bytes_b)).convert("RGB")
    diff = ImageChops.difference(img_a, img_b)
    stat = ImageStat.Stat(diff)
    mean = sum(stat.mean) / (len(stat.mean) * 255.0)
    return float(mean)


def image_bytes_ahash(img_bytes: bytes, size: int = 8) -> str:
    img = Image.open(io_bytes(img_bytes)).convert("L").resize((size, size))
    pixels = list(img.getdata())
    avg = sum(pixels) / len(pixels)
    bits = "".join("1" if px >= avg else "0" for px in pixels)
    return bits


def io_bytes(raw_bytes: bytes):
    from io import BytesIO

    return BytesIO(raw_bytes)
