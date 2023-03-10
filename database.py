import contextlib
import json
import multiprocessing
import time

import redis
import yadisk

from typing import Literal

from directory_worker import DirectoryWorker
from const import PUBSUB_VIDEO_CHANNEL_NAME


class RedisConnection:
    """
    Подключение к базе данных Redis.
    """
    connection = None

    def __new__(cls, *args, **kwargs):
        if cls.connection is None:
            cls.connection = super().__new__(cls)
        return cls.connection

    def __init__(self, host='127.0.0.1', port=6379, db_num=0):
        self._r = redis.Redis(host=host, port=port, db=db_num)
        self._connection = self

    def __getitem__(self, item):
        return json.loads(self._r.get(item))

    def __setitem__(self, key, value):
        self._r.set(key, json.dumps(value))

    def has(self, pattern: str) -> bool:
        return any(True for _ in self._r.scan_iter(pattern))

    def change_video_status(self, key: str, status_value: Literal['queued', 'in_progress', 'gathering', 'completed']):
        self._r.set(key, status_value)

    def subscribe(self, channel: str):
        p = self._r.pubsub()
        p.subscribe(channel)
        return p

    def publish(self, channel: str, message: str):
        self._r.publish(channel, message)


class DiskConnection(multiprocessing.Process):
    connection = None
    __y_disk_is_run = False

    def __new__(cls, *args, **kwargs):
        if cls.connection is None:
            cls.connection = super().__new__(cls)
        return cls.connection

    def __init__(self, token: str):
        super().__init__()
        self._conn: yadisk.YaDisk | None = None
        self._queue = multiprocessing.Queue()
        # print(id(q))
        self._token = token

    @property
    def queue(self):
        return self._queue

    def upload(self, src_path: str, dest_path: str):
        if not DirectoryWorker.exists(src_path):
            print('No video file found; cancel upload to cloud!')
            return

        self._mkdir_recursively(dest_path)

        try:
            src_path = DirectoryWorker.change_extension(src_path, 'tmp', rename_file=True)
            dest_path = DirectoryWorker.change_extension(dest_path, 'tmp')

            with contextlib.suppress(yadisk.exceptions.PathExistsError):
                self._conn.upload(
                    src_path,
                    dest_path,
                    overwrite=False,
                    n_retries=3
                )
                filename = DirectoryWorker.extract_filename(dest_path)
                filename = DirectoryWorker.change_extension(filename, 'mp4')
                self._conn.rename(dest_path, filename)

        except (yadisk.exceptions.ConflictError, yadisk.exceptions.LockedError) as e:
            print('Error while sending video to disk!')
            print(e)

    def _mkdir_recursively(self, path: str):
        dirs = DirectoryWorker.extract_directories(path)

        for d in dirs:
            if not self._conn.exists(d):
                self._conn.mkdir(d)

    def _seek(self):  # sourcery skip: use-named-expression
        subscription = RedisConnection().subscribe(PUBSUB_VIDEO_CHANNEL_NAME)
        while True:
            # if video_path := self._queue.get():
            #     print('Sending video...')
            #     self.upload(video_path, video_path)
            #     print('Completed')

            message = subscription.get_message(ignore_subscribe_messages=True)

            if message:
                video_path = message['data'].decode('utf-8')
                print('Sending video...')
                self.upload(video_path, video_path)
                print('Completed')
            time.sleep(1)

    def run(self) -> None:
        super().run()
        self._conn = yadisk.YaDisk(token=self._token)
        self._seek()

    def start(self) -> None:
        self.__y_disk_is_run = True
        super().start()

    @property
    def y_disk_is_run(self):
        return self.__y_disk_is_run

RedisConnection()
