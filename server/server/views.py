import multiprocessing

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import server.directory_methods as directory_methods
from server.const import DATE_FORMAT
from server.server.schemas.record import VideoRecorderInput
from server.server.schemas.record_regular import RegularVideoRecorderInput
from server.database import RedisConnection
from server.const import REDIS_SERVER, REDIS_PORT, REDIS_DB


app = FastAPI()

origins = [
    'http://localhost:8000',
    'http://localhost:8080',
    'http://localhost:8888',
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post('/')
async def start_record(video_params: VideoRecorderInput):
    """
    Post-запрос для записи видео. См. VideoRecorderInput для списка параметров.
    :param video_params: Входные данные для записи, извлекаемые из json-объекта тела запроса
    :return:
    """
    redis_db = RedisConnection(REDIS_SERVER, REDIS_PORT, REDIS_DB)

    # Записываю полученные значения из json в переменные
    path, name, comment, rtsp_url, fpm, config, intervals = video_params.dict().values()

    # Создаю папку, в которую будут записываться видео с изображениями
    video_path = f'{path}/{name}' if path != '' else name
    video_path = directory_methods.to_directory_friendly(video_path)
    directory_methods.mkdir(video_path)

    # Применяю функцию записи к каждому временному интервалу
    for i, interval in enumerate(intervals):
        task_db_key = f'videos:{name}:{i}'

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
            "with_audio": config['audio'],
        }

        # Запуск процесса записи
        print('Waiting...')


@app.post('/regular')
async def start_regular_record(video_params: RegularVideoRecorderInput):
    """
    Post-запрос для записи видео. См. VideoRecorderInput для списка параметров.
    :param video_params: Входные данные для записи, извлекаемые из json-объекта тела запроса
    :return:
    """
    redis_db = RedisConnection(REDIS_SERVER, REDIS_PORT, REDIS_DB)

    # Записываю полученные значения из json в переменные
    path, name, comment, rtsp_url, fpm, config, intervals, days = video_params.dict().values()

    video_path = f'{path}/{name}' if path != '' else name
    video_path = directory_methods.to_directory_friendly(video_path)

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
            "with_audio": config['audio'],
        }


@app.get('/')
async def load_records():
    redis_db = RedisConnection(REDIS_SERVER, REDIS_PORT, REDIS_DB)
    return redis_db.load_records_dict()



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
