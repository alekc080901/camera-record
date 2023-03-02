import os
import json

import uvicorn

from datetime import datetime
from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel

from transliterate import translit

from const import VIDEO_PATH, DATE_FORMAT
from video import count_images, calculate_image_number, record_video

app = FastAPI()

Path(VIDEO_PATH).mkdir(exist_ok=True)


class VideoRecorderInput(BaseModel):
    name: str
    comment: str
    rtsp_url: str
    date_from: datetime
    date_to: datetime
    fpm: int


@app.post('/')
def record(record_params: VideoRecorderInput):

    if not record_params.rtsp_url.startswith('rtsp://'):
        return {
            'error': True,
            'description': f'RTSP url must start with "rtsp://"! Got {record_params.rtsp_url}.'
        }

    record_params.name = translit(record_params.name, 'ru', reversed=True)

    video_path = os.path.join(VIDEO_PATH, record_params.name)

    # if os.path.exists(video_path):
    #     return {
    #         'error': True,
    #         'description': f'The name {record_params.name} has already been occupied!'
    #     }
    Path(video_path).mkdir(exist_ok=True)

    image_number = calculate_image_number(record_params.date_from, record_params.date_to, record_params.fpm)

    with open(os.path.join(video_path, 'video_info.json'), 'w') as file:
        info = {
            "name": record_params.name,
            "comment": record_params.comment,
            "rtsp_url": record_params.rtsp_url,
            "date_from": record_params.date_from.strftime(DATE_FORMAT),
            "date_to": record_params.date_to.strftime(DATE_FORMAT),
            "fpm": record_params.fpm,
            "image_number": image_number
        }
        json.dump(info, file)

    record_video(video_path, record_params.rtsp_url, record_params.fpm / 60, image_number)

    return {
        'date': (record_params.date_from, record_params.date_to)
    }


@app.get('/{name}')
async def get_progress(name):
    video_path = os.path.join(VIDEO_PATH, name)

    if os.path.exists(video_path):

        with open(os.path.join(video_path, 'video_info.json'), 'r') as file:
            video_info = json.load(file)
            image_number = video_info['image_number']

        return f'{count_images(video_path)}/{image_number}'

    return 'No such task is currently running.'


if __name__ == "__main__":
    uvicorn.run('server:app', host="127.0.0.1", reload=True, port=8000)
