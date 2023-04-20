import subprocess
import threading
import time

from datetime import datetime, timedelta

import server.directory_methods as directory_methods
from server.const import RECONNECT_DELAY_SECONDS, VIDEO_EXTENSION, \
    PUBSUB_VIDEO_CHANNEL_NAME, DATA_RANGE_INTERVAL_IN_MINUTES
from server.database import RedisConnection


def generate_day_label(day: datetime):
    idx_to_month = {
        1: 'January',
        2: 'February',
        3: 'March',
        4: 'April',
        5: 'May',
        6: 'June',
        7: 'July',
        8: 'August',
        9: 'September',
        10: 'October',
        11: 'November',
        12: 'December',
    }

    return f'{day.day} {idx_to_month[day.month]} {day.year}'


class VideoAudioRecorder(threading.Thread):
    """
    Процесс для записи видео камерой.
    :param rtsp_string: URL для подключения к камере
    :param name: Идентификатор записи
    :param start_date: Дата и время начала записи
    :param end_date: Дата и время конца записи
    :param fpm: Количество кадров в минуту, записываемых камерой
    :param db_key: Идентификатор записи в базе данных
    """

    def __init__(self, rtsp_string: str, name: str, path: str, start_date: datetime, end_date: datetime, db_key: str):
        super().__init__()
        self._rtsp = rtsp_string

        self._name = name
        self._path = path

        self._begins_at = start_date
        self._ends_at = end_date

        self._db = None
        self._db_key = db_key

    def _generate_date_ranges(self):
        delta = timedelta(minutes=DATA_RANGE_INTERVAL_IN_MINUTES)

        item = self._begins_at
        while item < self._ends_at:
            item += delta
            yield min(item, self._ends_at)

    def record(self):
        """
        Непосредственно процесс записи.
        Запись начинается с определенного момента времени (self.begins_at) и заканчивается
        в определенный момент времени (self.ends_at).
        :return:
        """
        self._db = RedisConnection()

        while datetime.now() < self._ends_at:
            date = datetime.now()

            subdirectory = generate_day_label(date)
            filename = f'{date.hour}_{date.minute:02}'.replace(':', '_') + f'.{VIDEO_EXTENSION}'

            directory_methods.mkdir(f'{self._path}/{subdirectory}')
            path = f'{self._path}/{subdirectory}/{filename}'

            remain_seconds = (datetime.now() - self._ends_at).seconds
            one_segment_time = min(DATA_RANGE_INTERVAL_IN_MINUTES * 60, remain_seconds)
            ffmpeg_record_string = f'ffmpeg -t {one_segment_time} ' \
                                   f'-rtsp_transport tcp -use_wallclock_as_timestamps 1 ' \
                                   f'-i {self._rtsp} -reset_timestamps 1 ' \
                                   f'-vcodec copy -pix_fmt yuv420p -threads 0 -crf 0 -preset ultrafast ' \
                                   f'-tune zerolatency -acodec pcm_s16le' \
                                   f' -strftime 1 "{path}"'

            print(path)
            p = subprocess.Popen(
                ffmpeg_record_string,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            p.wait()

            if p.returncode != 0:
                print(f'Error while recording video with audio! {self._name}')
                time.sleep(RECONNECT_DELAY_SECONDS)
                continue

            self._db.publish(PUBSUB_VIDEO_CHANNEL_NAME, f'{self._path}/{filename}')

        self._db.complete_task(self._db_key)
        print('End')

        return 0

    def run(self) -> None:
        self.record()
