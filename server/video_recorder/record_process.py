import time

import cv2

from datetime import datetime, timedelta
from typing import Union
import multiprocessing


import server.directory_methods as directory_methods
from server.const import RECONNECT_DELAY_SECONDS, VIDEO_EXTENSION, VIDEO_CODEC, \
    PUBSUB_VIDEO_CHANNEL_NAME, DATA_RANGE_INTERVAL_IN_MINUTES, DATE_FORMAT, TIME_FORMAT
from server.database import RedisConnection
from server.video_recorder.video_writer_manager import VideoWriterManager


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
                 fpm: Union[int, float], db_key: str, status_on_complete='completed'):
        super().__init__()
        self._rtsp = rtsp_string

        self._name = name
        self._path = path

        self._begins_at = start_date
        self._ends_at = end_date

        self._fps = fpm / 60

        self._camera_fps = None
        self._camera_res = None

        self._db = None
        self._db_key = db_key

        self.cap = None
        self.writer = None

    def _connect_to_camera(self):
        self.cap = cv2.VideoCapture(self._rtsp)

        # Параметры камеры
        self._camera_fps = self.cap.get(cv2.CAP_PROP_FPS)
        self._camera_res = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    def _generate_date_ranges(self):
        delta = timedelta(minutes=DATA_RANGE_INTERVAL_IN_MINUTES)

        item = datetime.now()
        while item < self._ends_at:
            item += delta
            yield min(item, self._ends_at)

    def _record_cycle(self, end_date: datetime):
        """
        Один цикл записи.
        :return: 0 в случае успеха. -1 в случае ошибки.
        """

        # Запись происходит до назначенного времени
        file_id = directory_methods.get_next_image_index(self._path)

        i = 1
        while datetime.now() < end_date:
            file_id += 1

            i += 1
            # Пропуск кадров, если необходимо (задан fps меньше fps камеры)
            for _ in range(int(1 / self._fps * self._camera_fps)):
                self.cap.grab()

            ret, frame = self.cap.retrieve()

            if not ret:
                print('Error while retrieving image!')
                return -1

            self.writer.write(frame)

        self.cap.release()
        time.sleep(2)
        return 0

    def record(self):
        """
        Непосредственно процесс записи.
        Запись начинается с определенного момента времени (self.begins_at) и заканчивается
        в определенный момент времени (self.ends_at).
        :return:
        """
        def handle_error(msg: str):
            print(msg)
            self._db.change_record_status(self._db_key, 'error')
            time.sleep(RECONNECT_DELAY_SECONDS)

        self._db = RedisConnection()

        while True:
            try:
                self._connect_to_camera()
            except Exception as e:
                handle_error(msg='Reconnecting to camera...')
                continue

            for date in self._generate_date_ranges():
                filename = f'{date.strftime(TIME_FORMAT)}.{VIDEO_EXTENSION}'

                # Данная странная конструкция служит для перезапуска процесса записи изображений в случае ошибки
                # Перезапуск производится с задержкой.
                # Стоит учитывать, что неудачное подключение к камере также занимает время.
                self.writer = VideoWriterManager(
                    writer_path=f'{self._path}/{filename}',
                    fps=self._camera_fps,
                    resolution=self._camera_res,
                )

                try:
                    print(date)
                    while self._record_cycle(date) != 0:
                        handle_error(msg='Reconnecting...')
                    break
                except Exception as e:
                    print(e)
                    handle_error(msg='Reconnecting to camera...')
                    self.writer.release()
                    continue
            # self._db.publish(PUBSUB_VIDEO_CHANNEL_NAME, f'{self._path}/{filename}')

        self._db.change_record_status(self._db_key, 'completed')
        print('End')

        return 0

    def run(self) -> None:
        super().run()
        self.record()
