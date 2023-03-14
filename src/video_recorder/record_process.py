import time

import cv2

import pause

from datetime import datetime
from typing import Union
import multiprocessing


import directory_methods
from src.const import RECONNECT_DELAY_SECONDS, VIDEO_EXTENSION, VIDEO_CODEC, PUBSUB_VIDEO_CHANNEL_NAME
from src.database import RedisConnection
from src.video_recorder.video_writer_manager import VideoWriterManager


class VideoRecorder(multiprocessing.Process):
    """
    Процесс для записи видео камерой.
    :param rtsp_string: URL для подключения к камере
    :param name: Идентификатор записи
    :param start_date: Дата и время начала записи
    :param end_date: Дата и время конца записи
    :param fpm: Количество кадров в минуту, записываемых камерой
    :param db_key: Идентификатор записи в базе данных
    """

    def __init__(self, rtsp_string: str, name: str, path: str, start_date: datetime, end_date: datetime,
                 fpm: Union[int, float], db_key: str):
        super().__init__()
        self._rtsp = rtsp_string

        self._name = name
        self._path = path
        self._video_name = f'{name}.{VIDEO_EXTENSION}'

        self._begins_at = start_date
        self._ends_at = end_date

        self._fps = fpm / 60

        self._camera_fps = None
        self._camera_res = None

        self._db = None
        self._db_key = db_key
        self._fourcc = cv2.VideoWriter_fourcc(*f'{VIDEO_CODEC}')

    def _record_cycle(self):
        """
        Один цикл записи.
        :return: 0 в случае успеха. -1 в случае ошибки.
        """
        cap = cv2.VideoCapture(self._rtsp)

        # Параметры камеры
        self._camera_fps = cap.get(cv2.CAP_PROP_FPS)
        self._camera_res = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        writer = VideoWriterManager(
            writer_path=f'{self._path}/{self._video_name}',
            codec=self._fourcc,
            fps=self._camera_fps,
            resolution=self._camera_res,
        )

        # Запись происходит до назначенного времени
        file_id = directory_methods.get_next_image_index(self._path)
        while datetime.now() < self._ends_at:
            file_id += 1

            # Пропуск кадров, если необходимо (задан fps меньше fps камеры)
            for _ in range(int(1 / self._fps * self._camera_fps)):
                cap.grab()

            ret, frame = cap.retrieve()

            if not ret:
                print('Error while retrieving image!')
                return -1

            writer.write(frame)

        cap.read()
        cap.release()
        writer.release()
        time.sleep(2)
        return 0

    def record(self):
        """
        Непосредственно процесс записи.
        Запись начинается с определенного момента времени (self.begins_at) и заканчивается
        в определенный момент времени (self.ends_at).
        :return:
        """
        print('Waiting...')
        pause.until(self._begins_at)
        print('Start!')

        self._db = RedisConnection()

        self._db.change_video_status(self._db_key, 'in_progress')

        # Данная странная конструкция служит для перезапуска процесса записи изображений в случае ошибки
        # Перезапуск производится с задержкой. Стоит учитывать, что неудачное подключение к камере также занимает время
        while True:
            try:
                while self._record_cycle() != 0:
                    print('Reconnecting...')
                    time.sleep(RECONNECT_DELAY_SECONDS)

                break
            except Exception as e:
                print(e)
                print('Reconnecting...')
                time.sleep(RECONNECT_DELAY_SECONDS)

        self._db.change_video_status(self._db_key, 'gathering')

        # self._db.publish(PUBSUB_VIDEO_CHANNEL_NAME, f'{self._path}/{self._video_name}')

        self._db.change_video_status(self._db_key, 'completed')

        print('End')

        return 0

    def run(self) -> None:
        super().run()
        self.record()
