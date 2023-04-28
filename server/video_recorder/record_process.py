import contextlib
import time

import cv2

from datetime import datetime, timedelta
from typing import Union
import multiprocessing

import server.directory_methods as directory_methods
from server.const import RECONNECT_DELAY_SECONDS, VIDEO_EXTENSION, \
    PUBSUB_VIDEO_CHANNEL_NAME
from server.database import RedisConnection
from server.video_recorder.video_writer_manager import VideoWriterManager


class VideoRecorder(multiprocessing.Process):
    """
    Процесс для записи видео камерой.
    Является процессом из библиотеки multiprocessing. Для записи используется библиотека OpenCV.
    :param rtsp: URL для подключения к камере
    :param name: Идентификатор записи
    :param start_date: Дата и время начала записи
    :param end_date: Дата и время конца записи
    :param fpm: Количество кадров в минуту, записываемых камерой
    :param db_key: Идентификатор записи в базе данных
    :param segment_time: Время одной записи (по умолчанию DEFAULT_SEGMENT_TIME из const.py), по истечении которого
    происходит разбиение

    :param self._cap: Объект подключения к камере VideoCapture из OpenCV
    :param self._fps: Количество кадров в секунду, записываемых камерой
    :param self._camera_fps: FPS камеры, получаемый при подключении к камере
    :param self._db: Указатель на базу данных Redis
    :param self._writer: Объект класса VideoWriterManager
    """

    def __init__(self, rtsp: str, name: str, path: str, start_date: datetime, end_date: datetime,
                 segment_time: int, db_key: str, fpm: Union[int, float] = None):
        super().__init__()
        self.rtsp = rtsp

        self.name = name
        self.path = path

        self.begins_at = start_date
        self.ends_at = end_date

        self.segment_time = segment_time

        self._fps = None if fpm is None else fpm / 60

        self._camera_fps = None
        self._camera_res = None

        self._db = None
        self.db_key = db_key

        self._cap = None
        self._writer = None

    def _connect_to_camera(self):
        """
        Попытка подключение к камере по rtsp.
        Обновляет параметры класса self._cap, self._camera_fps, self._camera_res.
        :return: True при успешном подключении; иначе False
        """
        try:
            self._cap = cv2.VideoCapture(self.rtsp)

            # Параметры камеры
            self._camera_fps = self._cap.get(cv2.CAP_PROP_FPS)
            self._camera_res = int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(
                self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            return self._cap.isOpened()
        except Exception as e:
            print(f'Can\'t connect to a camera! ({self.name})')
            return False

    def _record_cycle(self, end_date: datetime):
        """
        Один цикл записи.
        :return: 0 в случае успеха. -1 в случае ошибки.
        """
        self._db.change_record_status(self.db_key, 'in_progress')

        # Запись происходит до назначенного времени
        file_id = directory_methods.get_next_image_index(self.path)

        i = 1
        while datetime.now() < end_date:
            file_id += 1

            i += 1

            # Пропуск кадров, если необходимо (задан fps меньше fps камеры)
            for _ in range(int(1 / self._fps * self._camera_fps)):
                self._cap.grab()

            ret, frame = self._cap.retrieve()

            if not ret:
                print('Error while retrieving image!')
                return -1

            self._writer.write(frame)
        self._cap.release()
        time.sleep(2)
        return 0

    def _run_cycle(self, end_date):
        self._connect_to_camera()

        if self._fps is None:
            self._fps = self._camera_fps

        with contextlib.suppress(Exception):
            res = self._record_cycle(end_date)
            return res if res != -1 else None

    def record(self):
        """
        Непосредственно процесс записи.
        Запись начинается с определенного момента времени (self.begins_at) и заканчивается
        в определенный момент времени (self.ends_at).
        :return:
        """
        self._db = RedisConnection()

        while datetime.now() < self.ends_at:
            while not self._connect_to_camera():
                print(self.rtsp)
                print(f'Error on initial connection to camera! ({self.name})')
                time.sleep(RECONNECT_DELAY_SECONDS)

            date_now = datetime.now()
            filename = date_now.isoformat(timespec='seconds').replace(':', '_') + f'.{VIDEO_EXTENSION}'

            print(f'{self.path}/{filename}', self._camera_fps, self._camera_res)

            self._writer = VideoWriterManager(
                writer_path=f'{self.path}/{filename}',
                fps=self._camera_fps,
                resolution=self._camera_res,
            )

            end_date = date_now + timedelta(minutes=self.segment_time)
            while self._run_cycle(end_date) is None:
                print(f'Error {self.name}')
                self._db.change_record_status(self.db_key, 'error')
                time.sleep(RECONNECT_DELAY_SECONDS)

            self._writer.release()
            self._db.publish(PUBSUB_VIDEO_CHANNEL_NAME, f'{self.path}/{filename}')

        self._db.complete_task(self.db_key)
        print('End')

        return 0

    def run(self) -> None:
        super().run()
        self.record()
