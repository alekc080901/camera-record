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
    'http://localhost:8001',
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
async def start_record(rec: VideoRecorderInput):
    """
    Post-запрос для записи видео. См. VideoRecorderInput для списка параметров.
    :param rec: Входные данные для записи, извлекаемые из json-объекта тела запроса
    :return:
    """
    redis_db = RedisConnection(REDIS_SERVER, REDIS_PORT, REDIS_DB)

    # Создаю папку, в которую будут записываться видео с изображениями
    video_path = f'{rec.path}/{rec.name}' if rec.path != '' else rec.name
    video_path = directory_methods.to_directory_friendly(video_path)
    directory_methods.mkdir(video_path)

    # Применяю функцию записи к каждому временному интервалу
    for i, interval in enumerate(rec.intervals):
        task_db_key = f'videos:{rec.name}:{i}'

        # TODO: Добавить нормальную аннотацию типов через методы класса
        # Запись в БД
        redis_db[task_db_key] = {
            "name": rec.name,
            "comment": rec.comment,
            "rtsp_url": rec.rtsp_url,
            "path": video_path,
            "date_from": interval['date_from'].strftime(DATE_FORMAT),
            "date_to": interval['date_to'].strftime(DATE_FORMAT),
            "fpm": rec.fpm,
            "status": 'queued',
            "with_audio": rec.config.audio,
            "segment_time": rec.config.segment_time,
        }

        # Запуск процесса записи
        print('Waiting...')


@app.post('/regular')
async def start_regular_record(rec: RegularVideoRecorderInput):
    """
    Post-запрос для записи видео. См. VideoRecorderInput для списка параметров.
    :param rec: Входные данные для записи, извлекаемые из json-объекта тела запроса
    :return:
    """
    redis_db = RedisConnection(REDIS_SERVER, REDIS_PORT, REDIS_DB)

    video_path = f'{rec.path}/{rec.name}' if rec.path != '' else rec.name
    video_path = directory_methods.to_directory_friendly(video_path)

    for i, interval in enumerate(rec.intervals):
        task_id = f'regular:{rec.name}:{i}'

        # Запись в БД
        redis_db[task_id] = {
            "name": rec.name,
            "comment": rec.comment,
            "rtsp_url": rec.rtsp_url,
            "path": video_path,
            "time_from": interval['time_from'].strftime(DATE_FORMAT),
            "time_to": interval['time_to'].strftime(DATE_FORMAT),
            "fpm": rec.fpm,
            "status": 'queued',
            "days_of_week": rec.days_of_week,
            "with_audio": rec.config.audio,
            "segment_time": rec.config.segment_time,
        }


@app.get('/')
async def get_records():
    """
    Получение списка записей из БД
    :return:
    """
    redis_db = RedisConnection(REDIS_SERVER, REDIS_PORT, REDIS_DB)
    return redis_db.get_all_records()


@app.delete('/{name}')
async def delete_record(name: str):
    """
    Удаление записи с указанным в параметрах запроса именем
    :param name:
    :return:
    """
    redis_db = RedisConnection(REDIS_SERVER, REDIS_PORT, REDIS_DB)
    redis_db.delete_record(name)
