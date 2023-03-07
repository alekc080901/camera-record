import os

from pydantic import BaseModel, validator, Field
from typing import Dict, List
from datetime import datetime

from transliterate import translit

from database import db
from const import VIDEO_PATH


def to_directory_friendly(string: str):
    string = string.replace(' ', '_')
    return translit(string, 'ru', reversed=True)


class VideoRecorderInput(BaseModel):
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

    @validator("name")
    def name_must_be_unique(cls, name):
        video_path = f'{VIDEO_PATH}/{to_directory_friendly(name)}'
        if os.path.exists(video_path) or db.has(f'videos:{name}:*'):
            raise ValueError(f'The name {name} has already been occupied!')
        return name

    @validator("rtsp_url")
    def correct_rtsp_url(cls, url):
        if not url.startswith('rtsp://'):
            raise ValueError(f'RTSP url must start with "rtsp://"! Got {url}.')
        return url
