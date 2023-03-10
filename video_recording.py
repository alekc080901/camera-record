import time

import cv2

import pause

from datetime import datetime
from typing import Union
import multiprocessing

from const import RECONNECT_DELAY_SECONDS, VIDEO_EXTENSION, VIDEO_CODEC, PUBSUB_VIDEO_CHANNEL_NAME
from directory_worker import DirectoryWorker
from database import RedisConnection


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
        # self._disk_queue = disk_queue

    def calculate_workload(self) -> int:
        """
        Расчет предполагаемого количества изображений в записи от начала до конца видеосъемки.
        :return: Количество кадров
        """
        # TODO: Глупая идея. Избавиться
        return int((self._ends_at - self._begins_at).seconds * self._fps)

    def _record_cycle(self):
        """
        Один цикл записи.
        :return: 0 в случае успеха. -1 в случае ошибки.
        """
        cap = cv2.VideoCapture(self._rtsp)

        # Параметры камеры
        self._camera_fps = cap.get(cv2.CAP_PROP_FPS)
        self._camera_res = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Запись происходит до назначенного времени
        file_id = DirectoryWorker.get_next_image_index(self._path)
        while datetime.now() < self._ends_at:
            filename = f'{self._path}/{file_id:10d}.jpeg'
            file_id += 1

            # Пропуск кадров, если необходимо (задан fps меньше fps камеры)
            for _ in range(int(1 / self._fps * self._camera_fps)):
                cap.grab()

            ret, frame = cap.retrieve()

            if not ret:
                print('Error while retrieving image!')
                return -1

            im_written = cv2.imwrite(filename, frame)

            if not im_written:
                print('Error while writing image!')
                return -1

        cap.read()
        cap.release()
        time.sleep(1)
        return 0

    def _write_images_in_video(self):
        """
        Собирает все изображения в директории в одно видео формата .mp4. Предполагается, что
        изображения в директории уже отсортированы.
        :return:
        """
        # Подсчет параметров камеры (если запись не производилась, но изображения в директории есть)
        if self._camera_fps is None or self._camera_res is None:
            cap = cv2.VideoCapture(self._rtsp)
            self._camera_fps = cap.get(cv2.CAP_PROP_FPS)
            self._camera_res = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        fourcc = cv2.VideoWriter_fourcc(*f'{VIDEO_CODEC}')

        writer = cv2.VideoWriter(
            f'{self._path}/{self._video_name}',
            fourcc,
            self._camera_fps,
            self._camera_res,
        )
        for filename in DirectoryWorker.get_images(self._path):
            path = f'{self._path}/{filename}'
            image = cv2.imread(path)

            writer.write(image)

        writer.release()

    def _delete_all_images(self):
        """
        Удаляет все изображения в директории.
        :return:
        """
        DirectoryWorker.delete_images(self._path)

    def record(self):
        """
        Непосредственно процесс записи. Запись начинается с определенного момента времени (self.begins) и заканчивается
        в определенный момент времени (self.ends).
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

        print('Transforming to video...')
        self._write_images_in_video()
        # self._delete_images()

        # self._disk_queue.put(f'{self._path}/{self._video_name}')
        self._db.publish(PUBSUB_VIDEO_CHANNEL_NAME, f'{self._path}/{self._video_name}')

        self._db.change_video_status(self._db_key, 'completed')

        print('End')

        return 0

    def run(self) -> None:
        super().run()
        self.record()
