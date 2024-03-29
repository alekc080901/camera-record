import contextlib
import os
import subprocess
import threading
import time

from datetime import datetime, timedelta

import server.directory_methods as directory_methods
from server.const import RECONNECT_DELAY_SECONDS, VIDEO_EXTENSION, \
    PUBSUB_VIDEO_CHANNEL_NAME
from server.database import RedisConnection


class VideoAudioRecorder(threading.Thread):
    """
    Процесс для записи видео камерой со звуком.
    Является потоком из библиотеки threading. Для записи используется библиотека subprocess и утилита ffmpeg.
    :param rtsp: URL для подключения к камере
    :param name: Идентификатор записи
    :param start_date: Дата и время начала записи
    :param end_date: Дата и время конца записи
    :param db_key: Идентификатор записи в базе данных
    :param segment_time: Время одной записи (по умолчанию DEFAULT_SEGMENT_TIME из const.py), по истечении которого
    происходит разбиение

    :param self._db: Указатель на базу данных Redis
    """

    def __init__(self, rtsp: str, name: str, path: str, start_date: datetime, segment_time: int,
                 end_date: datetime, db_key: str):
        super().__init__()
        self.rtsp = rtsp

        self.name = name
        self.path = path

        self.begins_at = start_date
        self.ends_at = end_date

        self._db = None
        self.db_key = db_key

        self.segment_time = segment_time

    def record(self):
        """
        Непосредственно процесс записи.
        Запись начинается с определенного момента времени (self.begins_at) и заканчивается
        в определенный момент времени (self.ends_at).
        :return:
        """
        self._db = RedisConnection()

        while datetime.now() < self.ends_at:
            date = datetime.now()

            filename = f'{date.hour}_{date.minute:02}'.replace(':', '_') + f'.{VIDEO_EXTENSION}'

            directory_methods.mkdir(f'{self.path}')
            path = f'{self.path}/{filename}'

            remain_seconds = (self.ends_at - datetime.now()).seconds
            one_segment_time = min(self.segment_time * 60, remain_seconds)
            print(remain_seconds, one_segment_time)
            ffmpeg_record_string = f'ffmpeg -t {one_segment_time} ' \
                                   f'-rtsp_transport tcp -use_wallclock_as_timestamps 1 ' \
                                   f'-i {self.rtsp} -reset_timestamps 1 ' \
                                   f'-vcodec copy -pix_fmt yuv420p -threads 0 -crf 0 -preset ultrafast ' \
                                   f'-tune zerolatency -acodec pcm_s16le' \
                                   f' -strftime 1 "{path}" -y'
            print(path)
            p = subprocess.Popen(
                ffmpeg_record_string,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
            )

            # Добавление работающих процессов в теории должно было стать частью фичи по их удалению
            # self._db.add_running_process(self.db_key, p.pid, self.path)
            with contextlib.suppress(subprocess.TimeoutExpired):
                p.wait(timeout=one_segment_time + 10)  # Ждем на 10 секунд дольше
            # self._db.complete_process(self.db_key, p.pid)

            if p.returncode is not None and p.returncode != 0:
                print(f'Error while recording video with audio! {self.name}')
                time.sleep(RECONNECT_DELAY_SECONDS)
                continue

            self._db.publish(PUBSUB_VIDEO_CHANNEL_NAME, f'{self.path}/{filename}')

        self._db.complete_task(self.db_key)
        print('End')

        return 0

    def run(self) -> None:
        self.record()
