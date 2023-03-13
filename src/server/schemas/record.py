import cv2

from pydantic import BaseModel, validator, Field
from typing import Dict, List
from datetime import datetime

from transliterate import translit


def to_directory_friendly(string: str) -> str:
    """
    Переводит русское название в английское и заменяет пробелы нижним подчеркиванием.
    :param string: Строка
    :return: Обработанная строка
    """
    string = string.replace(' ', '_')
    return translit(string, 'ru', reversed=True)


class VideoRecorderInput(BaseModel):
    """
    JSON-схема post-запроса записи видео.
    :param name: Идентификатор записи
    :param comment: Комментарий к записи
    :param rtsp_url: URL для подключения к камере
    :param fpm: Количество кадров в минуту, записываемых камерой
    :param intervals: Список временных промежутков (от и до), в которые необходимо производить запись у заданной
    видеокамеры
    """
    path: str = Field(..., max_length=100)
    name: str = Field(..., max_length=100)
    comment: str = Field(..., max_length=500)
    rtsp_url: str = Field(..., max_length=200)
    fpm: float = Field(..., gt=0)
    intervals: List[Dict[str, datetime]]

    @validator('name')
    def name_must_not_be_empty(cls, name):
        trash_symbols = ('\t', '\n', '\v', '\f', ' ')
        if all(s in trash_symbols for s in name):
            raise ValueError('Name must not be empty or contain only insignificant symbols!')
        return name

    # @validator("name")
    # def name_must_be_unique(cls, name, values):
    #     db = RedisConnection.connection
    #
    #     video_path = f'{values["path"]}/{to_directory_friendly(name)}'
    #     if DirectoryWorker.exists(video_path) or db.has(f'videos:{name}:*'):
    #         raise ValueError(f'The name {name} has already been occupied!')
    #     return name

    @validator("rtsp_url")
    def correct_rtsp_url(cls, url):
        if not cv2.VideoCapture(url).isOpened():
            raise ValueError(f"Couldn't connect via given rtsp url! Url: {url}")
        return url

    @validator("path")
    def correct_path(cls, path):
        return path.strip('/\\')
