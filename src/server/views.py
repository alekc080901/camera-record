from fastapi import FastAPI

import directory_methods
import wait_functions
from src.const import DATE_FORMAT
from src.server.schemas.record import VideoRecorderInput
from src.server.schemas.record_regular import RegularVideoRecorderInput
from video_recorder.record_process import VideoRecorder
from src.database import RedisConnection
from src.const import REDIS_SERVER, REDIS_PORT, REDIS_DB


app = FastAPI()


@app.post('/')
async def start_record(video_params: VideoRecorderInput):
    """
    Post-запрос для записи видео. См. VideoRecorderInput для списка параметров.
    :param video_params: Входные данные для записи, извлекаемые из json-объекта тела запроса
    :return:
    """
    redis_db = RedisConnection(REDIS_SERVER, REDIS_PORT, REDIS_DB)

    # Записываю полученные значения из json в переменные
    path, name, comment, rtsp_url, fpm, intervals = video_params.dict().values()

    # Создаю папку, в которую будут записываться видео с изображениями
    name_of_dir = directory_methods.to_directory_friendly(name)
    video_path = f'{path}/{name_of_dir}'
    directory_methods.mkdir(video_path)

    # Применяю функцию записи к каждому временному интервалу
    for i, interval in enumerate(intervals):
        task_db_key = f'videos:{name}:{i}'
        rec = VideoRecorder(
            db_key=task_db_key,
            rtsp_string=rtsp_url,
            name=name_of_dir,
            path=video_path,
            fpm=fpm,
            start_date=interval['date_from'],
            end_date=interval['date_to'],
        )

        # TODO: Добавить нормальную аннотацию типов через методы класса
        # Запись в БД
        redis_db[task_db_key] = {
            "name": name,
            "comment": comment,
            "rtsp_url": rtsp_url,
            "path": video_path,
            "date_from": interval['date_from'].strftime(DATE_FORMAT),
            "date_to": interval['date_to'].strftime(DATE_FORMAT),
            "fpm": fpm,
            "status": "queued",
        }

        # Запуск процесса записи
        print('Waiting...')
        await wait_functions.until_async(interval['date_from'])

        rec.start()
        redis_db.change_video_status(task_db_key, 'in_progress')


@app.post('/regular')
async def start_record(video_params: RegularVideoRecorderInput):
    """
    Post-запрос для записи видео. См. VideoRecorderInput для списка параметров.
    :param video_params: Входные данные для записи, извлекаемые из json-объекта тела запроса
    :return:
    """
    redis_db = RedisConnection(REDIS_SERVER, REDIS_PORT, REDIS_DB)

    # Записываю полученные значения из json в переменные
    path, name, comment, rtsp_url, fpm, intervals, days = video_params.dict().values()

    name_of_dir = directory_methods.to_directory_friendly(name)
    video_path = f'{path}/{name_of_dir}'

    for i, interval in enumerate(intervals):
        task_id = f'regular:{name}:{i}'

        # Запись в БД
        redis_db[task_id] = {
            "name": name,
            "comment": comment,
            "rtsp_url": rtsp_url,
            "path": video_path,
            "time_from": interval['time_from'].strftime(DATE_FORMAT),
            "time_to": interval['time_to'].strftime(DATE_FORMAT),
            "fpm": fpm,
            "status": "queued",
            "days_of_week": days,
        }


@app.get('/{name}')
async def get_progress(name):
    """
    Отображение прогресса записи по ее идентификатору. Пока первого интервала
    :param name: Идентификатор записи
    :return: Строчка с прогрессом
    """
    # TODO: Сделать функцию адекватной и рабочей
    video_db_key = f'videos:{name}:0'

    redis_db = RedisConnection(REDIS_SERVER, REDIS_PORT, REDIS_DB)

    if redis_db[video_db_key]:
        return f'{directory_methods.count_images(redis_db[video_db_key]["path"])}/' \
               f'{redis_db[video_db_key]["image_number"]}'

    return 'No such task is currently running.'
