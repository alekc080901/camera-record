import multiprocessing

import uvicorn
import yadisk

from pathlib import Path

from fastapi import FastAPI

from const import DATE_FORMAT
from schemas.record import VideoRecorderInput, to_directory_friendly
from video_recording import VideoRecorder
from directory_worker import DirectoryWorker
from database import RedisConnection, DiskConnection
from const import REDIS_SERVER, REDIS_PORT, REDIS_DB, CLOUD_ACCESS_TOKEN

# queue = multiprocessing.Queue()

# yandex_disk = DiskConnection(token=CLOUD_ACCESS_TOKEN)
redis_db = RedisConnection(REDIS_SERVER, REDIS_PORT, REDIS_DB)

yandex_disk = DiskConnection(token=CLOUD_ACCESS_TOKEN)

app = FastAPI()


@app.post('/')
async def start_record(video_params: VideoRecorderInput):
    # yandex_disk = DiskConnection(token=CLOUD_ACCESS_TOKEN)
    # if not yandex_disk.y_disk_is_run:
    #     print('+')
    #     yandex_disk.start()

    """
    Post-запрос для записи видео. См. VideoRecorderInput для списка параметров.
    :param video_params: Входные данные для записи, извлекаемые из json-объекта тела запроса
    :return:
    """
    # Записываю полученные значения из json в переменные
    path, name, comment, rtsp_url, fpm, intervals = video_params.dict().values()

    # Создаю папку, в которую будут записываться видео с изображениями
    name_of_dir = to_directory_friendly(name)
    video_path = f'{path}/{name_of_dir}'
    Path(video_path).mkdir(parents=True, exist_ok=True)

    # Применяю функцию записи к каждому временному интервалу
    for i, interval in enumerate(intervals):
        task_id = f'videos:{name}:{i}'
        rec = VideoRecorder(
            rtsp_string=rtsp_url,
            name=name_of_dir,
            path=video_path,
            fpm=fpm,
            start_date=interval['date_from'],
            end_date=interval['date_to'],
            db_key=task_id,
            # disk_queue=yandex_disk.queue,
        )
        # print(id(queue))
        image_number = rec.calculate_workload()

        # Запись в БД
        redis_db[task_id] = {
            "comment": comment,
            "rtsp_url": rtsp_url,
            "path": video_path,
            "date_from": interval['date_from'].strftime(DATE_FORMAT),
            "date_to": interval['date_to'].strftime(DATE_FORMAT),
            "fpm": fpm,
            "image_number": image_number,
            "status": "queued",
        }
        # Запуск процесса записи
        rec.start()


@app.get('/{name}')
async def get_progress(name):
    """
    Отображение прогресса записи по ее идентификатору. Пока первого интервала
    :param name: Идентификатор записи
    :return: Строчка с прогрессом
    """
    # TODO: Сделать функцию адекватной и рабочей
    video_db_key = f'videos:{name}:0'

    if redis_db[video_db_key]:
        return f'{DirectoryWorker.count_images(redis_db[video_db_key]["path"])}/' \
               f'{redis_db[video_db_key]["image_number"]}'

    return 'No such task is currently running.'


if __name__ == "__main__":
    yandex_disk.start()
    uvicorn.run('server:app', host="127.0.0.1", reload=True, port=8888)
