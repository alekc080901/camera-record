import os

import cv2

import pause

from datetime import datetime
from typing import Union
import multiprocessing

from const import IMAGE_EXTENSIONS


def count_images(path: str) -> int:
    files = os.listdir(path)
    image_files = [file for file in files if '.' in file and file.split('.')[-1] in IMAGE_EXTENSIONS]
    return len(image_files)


def get_image_index(path: str) -> int:
    files = os.listdir(path)
    numbers = [int(file.split('.')[0]) for file in files]
    return max(numbers) + 1 if len(files) > 0 else 0


class VideoRecorder(multiprocessing.Process):
    def __init__(self, rtsp_string: str, video_path: str, start_date: datetime, end_date: datetime, fpm: Union[int, float]):
        super().__init__()
        self.rtsp = rtsp_string

        self.path = video_path

        self.begins = start_date
        self.ends = end_date

        self.fps = fpm / 60

    def calculate_workload(self) -> int:
        return int((self.ends - self.begins).seconds * self.fps)

    def record(self):
        print('Waiting...')
        pause.until(self.begins)
        print('Start!')

        cap = cv2.VideoCapture(self.rtsp)

        camera_fps = cap.get(cv2.CAP_PROP_FPS)

        file_id = get_image_index(self.path)
        while datetime.now() < self.ends:
            for _ in range(int(1 / self.fps * camera_fps)):
                cap.grab()

            ret, frame = cap.retrieve()

            if ret:
                cv2.imwrite(f'{self.path}/{file_id}.jpeg', frame)
            else:
                print('VideoCapture returned something bad.')

            file_id += 1
        print('End.')
        cap.read()
        cap.release()

    def run(self) -> None:
        super().run()
        self.record()
