import contextlib
import multiprocessing
import time

import yadisk

import server.directory_methods as directory_methods
from server.const import PUBSUB_VIDEO_CHANNEL_NAME, VIDEO_EXTENSION
from server.database import RedisConnection


class DiskConnection(multiprocessing.Process):
    """
    Класс осуществляет запись на Яндекс Диск (в данном случае запись видео).
    Singleton.
    """
    connection = None

    def __new__(cls, *args, **kwargs):
        if cls.connection is None:
            cls.connection = super().__new__(cls)
        return cls.connection

    def __init__(self, token: str):
        super().__init__()
        self._conn: yadisk.YaDisk | None = None
        self._token = token

    def upload_video(self, src_path: str, dest_path: str):
        """
        Отправляет видео на Яндекс диск
        :param src_path: Путь до видео
        :param dest_path: Конечный путь видео на диске
        :return:
        """
        if not directory_methods.exists(src_path):
            print('No file found; cancel upload to cloud!')
            return

        try:
            self._mkdir_recursively(dest_path)

            src_path = directory_methods.change_extension(src_path, 'tmp', rename_file=True)
            dest_path = directory_methods.change_extension(dest_path, 'tmp')

            if not self._conn.exists(dest_path):
                self._conn.upload(
                    src_path,
                    dest_path,
                    overwrite=False,
                    n_retries=3
                )
                filename = directory_methods.extract_filename(dest_path)
                filename = directory_methods.change_extension(filename, VIDEO_EXTENSION)
                self._conn.rename(dest_path, filename)

        except (yadisk.exceptions.ConflictError, yadisk.exceptions.LockedError, PermissionError) as e:
            print('Error while sending to disk!')
            print(e)
        except (Exception) as e:
            print(f'Unknown exception! {dest_path}')
            print(e)

    def _mkdir_recursively(self, path: str):
        """
        Создает вложенные директории на Яндекс диске
        :param path: Путь до файла/папки, из которого извлекаются необходимые для создания директории
        :return:
        """
        dirs = directory_methods.extract_directories(path)

        for d in dirs:
            if not self._conn.exists(d):
                self._conn.mkdir(d)

    def _seek(self):
        """
        Поиск готовых для отправки видео через систему publisher-subscriber Redis
        :return:
        """
        subscription = RedisConnection().subscribe(PUBSUB_VIDEO_CHANNEL_NAME)
        while True:
            if message := subscription.get_message(ignore_subscribe_messages=True):
                video_path = message['data'].decode('utf-8')
                print('Sending video...')
                self.upload_video(video_path, video_path)
                print('Completed')
            time.sleep(1)

    def run(self) -> None:
        super().run()
        self._conn = yadisk.YaDisk(token=self._token)
        self._seek()


if __name__ == '__main__':
    yandex_disk = DiskConnection(token='y0_AgAAAAALeWngAAk_4QAAAADhNY13bDy5DG7RRCeiby8aDYpzelmB_wY')
    yandex_disk._conn = yadisk.YaDisk(token='y0_AgAAAAALeWngAAk_4QAAAADhNY13bDy5DG7RRCeiby8aDYpzelmB_wY')

    import glob

    for file in glob.glob('../../Exchange/Planeta/20 April 2023/*.mkv') + glob.glob('../../Exchange/Planeta/20 April 2023/*.tmp'):
        print(file, file[6:])
        yandex_disk.upload_video(file, file[6:])
