import os
import sys
import time

import cv2

import pause

from datetime import datetime
from typing import Union
import multiprocessing

from const import IMAGE_EXTENSIONS, OPENCV_CRASH_LIMIT, VIDEO_PATH
from database import db


def count_images(path: str) -> int:
    files = os.listdir(path)
    image_files = [file for file in files if '.' in file and file.split('.')[-1] in IMAGE_EXTENSIONS]
    return len(image_files)


def get_image_index(path: str) -> int:
    files = os.listdir(path)
    numbers = [int(file.split('.')[0]) for file in files]
    return max(numbers) + 1 if len(files) > 0 else 0


class VideoRecorder(multiprocessing.Process):
    records = []

    def __init__(self, rtsp_string: str, name: str, start_date: datetime, end_date: datetime,
                 fpm: Union[int, float], db_key: str):
        super().__init__()
        self.rtsp = rtsp_string

        self.name = name
        self.path = f'{VIDEO_PATH}/{name}'

        self.begins = start_date
        self.ends = end_date

        self.fps = fpm / 60

        self._camera_fps = None
        self._camera_res = None

        self.db_key = db_key

        VideoRecorder.records.append(self)

    def calculate_workload(self) -> int:
        return int((self.ends - self.begins).seconds * self.fps)

    def _record_cycle(self):
        cap = cv2.VideoCapture(self.rtsp)


        if not cap.isOpened():
            raise cv2.error('Error on connection to camera!')

        self.camera_fps = cap.get(cv2.CAP_PROP_FPS)
        self.camera_res = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        file_id = get_image_index(self.path)
        while datetime.now() < self.ends:
            file_id += 1

            for _ in range(int(1 / self.fps * self.camera_fps)):
                cap.grab()

            ret, frame = cap.retrieve()

            if ret:
                im_written = cv2.imwrite(f'{self.path}/{file_id:10d}.jpeg', frame)
                if im_written:
                    continue

            return -1

        cap.read()
        return 0

    def _images_to_video(self):
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')

        writer = cv2.VideoWriter(f'{self.path}/{self.name}.mp4', fourcc, self._camera_fps, self._camera_res)

        for filename in os.listdir(self.path):
            if filename.split('.')[-1] in IMAGE_EXTENSIONS:
                path = f'{self.path}/{filename}'
                image = cv2.imread(path)
                writer.write(image)

        writer.release()

    def _delete_images(self):
        for filename in os.listdir(self.path):
            if filename.split('.')[-1] in IMAGE_EXTENSIONS:
                os.remove(f'{self.path}/{filename}')

    def record(self):
        print('Waiting...')
        pause.until(self.begins)
        db.change_video_status(self.db_key, 'in_progress')
        print('Start!')

        try:
            while self._record_cycle() != 0:
                pass
        except Exception:
            pass

        db.change_video_status(self.db_key, 'completed')

        print('Transforming to video...')
        self._images_to_video()
        self._delete_images()
        print('Completed!')

        return 0

    def run(self) -> None:
        super().run()
        self.record()
