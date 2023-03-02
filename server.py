import os

import uvicorn

from datetime import datetime
from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel

from const import VIDEO_PATH
from video import count_images

app = FastAPI()

Path(VIDEO_PATH).mkdir(exist_ok=True)


class VideoRecorderInput(BaseModel):
    name: str
    comment: str
    rtsp_route: str
    date_from: datetime
    date_to: datetime
    fpm: int


@app.post('/')
async def record(record_params: VideoRecorderInput):
    video_path = os.path.join(VIDEO_PATH, record_params.name)

    if os.path.exists(video_path):
        return {
            'error': True,
            'description': f'The name {record_params.name} has already been occupied!'
        }

    Path(video_path).mkdir()

    return {
        'date': (record_params.date_from, record_params.date_to)
    }


@app.get('/{name}')
async def get_progress(name):
    video_path = os.path.join(VIDEO_PATH, name)
    if os.path.exists(video_path):
        return count_images(video_path)

    return 'No such task is currently running.'


if __name__ == "__main__":
    uvicorn.run('server:app', host="127.0.0.1", reload=True, port=8000)
