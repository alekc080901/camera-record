import os

import cv2

from const import IMAGE_EXTENSIONS

from datetime import datetime


def count_images(path: str) -> int:
    files = os.listdir(path)
    image_files = [file for file in files if '.' in file and file.split('.')[-1] in IMAGE_EXTENSIONS]
    return len(image_files)


def calculate_image_number(date1: datetime, date2: datetime, fpm: int) -> int:
    return int((date2 - date1).seconds / 60 * fpm)

def recording(rtsp: str, fps):
    cap = cv2.VideoCapture(rtsp)

    input_fps = cap.get(cv2.CAP_PROP_FPS)

    while True:
        ret, frame = cap.read()
        if ret:
            cv2.imwrite(path, frame)
