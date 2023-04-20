from pydantic import validator
from typing import Dict, List
from datetime import datetime

from server.server.schemas.base import BaseRecord


class VideoRecorderInput(BaseRecord):
    """
    JSON-схема post-запроса записи видео.
    :param name: Идентификатор записи
    :param comment: Комментарий к записи
    :param rtsp_url: URL для подключения к камере
    :param fpm: Количество кадров в минуту, записываемых камерой
    :param intervals: Список временных промежутков (от и до), в которые необходимо производить запись у заданной
    видеокамеры
    """
    intervals: List[Dict[str, datetime]]

    @validator("intervals")
    def correct_intervals(cls, intervals):
        for interval in intervals:

            if len(interval.keys()) != 2:
                raise ValueError("Wrong number of keys in interval!")

            if 'date_from' not in interval or 'date_to' not in interval:
                raise ValueError("Some keys missing in interval!")

            if interval['date_to'].timestamp() < datetime.now().timestamp() or interval['date_to'] < interval['date_from']:
                raise ValueError("Incorrect timestamp!")

        return intervals
