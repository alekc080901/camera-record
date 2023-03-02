import os

import numpy as np
import cv2

from const import IMAGE_EXTENSIONS

from datetime import datetime


def count_images(path: str) -> int:
    files = os.listdir(path)
    image_files = [file for file in files if '.' in file and file.split('.')[-1] in IMAGE_EXTENSIONS]
    return len(image_files)


def calculate_image_number(date1: datetime, date2: datetime, fpm: int) -> int:
    return int((date2 - date1).seconds / 60 * fpm)


def record_video(dest: str, rtsp: str, fps: float, goal: int):
    cap = cv2.VideoCapture(rtsp)

    camera_fps = cap.get(cv2.CAP_PROP_FPS)

    for i in range(goal):
        for _ in range(int(1 / fps * camera_fps)):
            cap.grab()

        ret, frame = cap.retrieve()

        if ret:
            cv2.imwrite(f'{dest}/{i}.jpeg', frame)
        else:
            print('VideoCapture returned something bad.')
