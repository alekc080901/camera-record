import multiprocessing
import time

from datetime import datetime, timedelta

import directory_methods
import src.directory_methods
from src.video_recorder.record_process import VideoRecorder
from src.database import RedisConnection
from src.const import DATE_FORMAT


class RegularRecording(multiprocessing.Process):

    SCAN_INTERVAL_SECONDS = 60
    TIME_FORMAT = '%H:%M:%S'

    def __init__(self):
        super().__init__()

    def _seek(self):
        db = RedisConnection()
        while True:
            tasks = db.get_all('regular:*')

            now = datetime.now()
            for task in tasks:
                info = db[task]

                # Запускать процесс, если:
                # 1) совпадает день недели;
                # 2) процесс еще не запущен;
                # 3) процесс находится во временном промежутке запуска.
                if now.weekday() in info['days_of_week'] and \
                        info['status'] != 'in_progress' and \
                        datetime.strptime(info['time_from'], DATE_FORMAT).time() <= now.time() \
                        <= datetime.strptime(info['time_to'], DATE_FORMAT).time():

                    start = datetime(now.year, now.month, now.day, now.hour, now.minute, now.second)
                    end_time = datetime.strptime(info['time_to'], DATE_FORMAT).time()

                    tmp = start + timedelta(days=1) if end_time < start.time() else start

                    end = datetime(tmp.year, tmp.month, tmp.day, end_time.hour, end_time.minute, end_time.second)

                    process = VideoRecorder(
                        rtsp_string=info['rtsp_url'],
                        name=info['name'],
                        path=info['path'],
                        fpm=info['fpm'],
                        start_date=start,
                        end_date=end,
                        db_key=task,
                    )

                    directory_methods.mkdir(info['path'])

                    process.start()
                    db.change_video_status(task, 'in_progress')

            time.sleep(self.SCAN_INTERVAL_SECONDS)

    def run(self):
        super().run()
        self._seek()
