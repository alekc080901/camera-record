import multiprocessing
import time as time_

from datetime import datetime, timedelta, time

import server.directory_methods as directory_methods
from server.database import RedisConnection
from server.const import DATE_FORMAT
from server.video_recorder.record_factory import create_recorder


def str_to_time(time_str: str) -> time:
    return datetime.strptime(time_str, DATE_FORMAT).time()


def str_to_datetime(datetime_str: str) -> datetime:
    return datetime.strptime(datetime_str, DATE_FORMAT)


class RecordLauncher:
    @staticmethod
    def seek_for_record(db: RedisConnection, today: datetime):
        def date_in_interval(start: datetime, end: datetime):
            return start < today < end

        tasks = db.get_keys('videos:*')

        for task in tasks:
            info = db[task]

            # Запускать процесс, если:
            # 1) Процесс не запускался;
            # 2) процесс находится во временном промежутке запуска.
            if not db.task_is_running(task) and \
                    date_in_interval(str_to_datetime(info['date_from']), str_to_datetime(info['date_to'])):
                return task, info

    @staticmethod
    def start_record_process(key: str, name: str, rtsp: str, path: str, fpm: int, today: datetime, end_date: datetime,
                             with_audio=False):
        start_date = today

        process = create_recorder(
            audio=with_audio,
            rtsp_string=rtsp,
            name=name,
            path=path,
            fpm=fpm,
            start_date=start_date,
            end_date=end_date,
            db_key=key,
        )

        directory_methods.mkdir(path)
        process.start()


class RegularRecordLauncher:
    @staticmethod
    def seek_for_regular_record(db: RedisConnection, today: datetime):
        def today_is_day_of_week(permitted_days: list[int]) -> bool:
            return today.weekday() in permitted_days

        def time_in_interval(now: time, start: time, end: time) -> bool:
            if start < end:
                return start <= now <= end

            return now >= start and now >= end or now <= start and now <= end

        tasks = db.get_keys('regular:*')

        for task in tasks:
            info = db[task]

            # Запускать процесс, если:
            # 1) совпадает день недели;
            # 2) процесс еще не запущен;
            # 3) процесс находится во временном промежутке запуска.
            if today_is_day_of_week(info['days_of_week']) and \
                    not db.task_is_running(task) and \
                    time_in_interval(today.time(), str_to_time(info['time_from']), str_to_time(info['time_to'])):
                return task, info

    @staticmethod
    def start_record_process(key: str, name: str, rtsp: str, path: str, fpm: int, today: datetime, end_time: time,
                             with_audio=False):
        start = datetime(today.year, today.month, today.day, today.hour, today.minute, today.second)

        tmp = start + timedelta(days=1) if end_time < start.time() else start
        end = datetime(tmp.year, tmp.month, tmp.day, end_time.hour, end_time.minute, end_time.second)

        process = create_recorder(
            audio=with_audio,
            rtsp_string=rtsp,
            name=name,
            path=path,
            fpm=fpm,
            start_date=start,
            end_date=end,
            db_key=key,
        )

        directory_methods.mkdir(path)

        process.start()


class RecordManager(multiprocessing.Process):
    SCAN_INTERVAL_SECONDS = 10
    TIME_FORMAT = '%H:%M:%S'

    def __init__(self):
        super().__init__()

    def _seek(self):
        db = RedisConnection()
        while True:
            now = datetime.now()
            if ret := RegularRecordLauncher.seek_for_regular_record(db, now):
                key, info = ret

                print(f'Start {info["name"]}')
                RegularRecordLauncher.start_record_process(
                    key=key,
                    name=info['name'],
                    path=info['path'],
                    fpm=info['fpm'],
                    rtsp=info['rtsp_url'],
                    today=now,
                    end_time=str_to_time(info['time_to']),
                    with_audio=info['with_audio'],
                )
                db.init_task(key)
                continue

            if ret := RecordLauncher.seek_for_record(db, now):
                key, info = ret

                print(f'Start {info["name"]}')
                RecordLauncher.start_record_process(
                    key=key,
                    name=info['name'],
                    path=info['path'],
                    fpm=info['fpm'],
                    rtsp=info['rtsp_url'],
                    today=now,
                    end_date=str_to_datetime(info['date_to']),
                    with_audio=info['with_audio'],
                )
                db.init_task(key)
                continue

            time_.sleep(self.SCAN_INTERVAL_SECONDS)

    def run(self):
        super().run()
        self._seek()
