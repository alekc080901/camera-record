import os

import uvicorn

from datetime import datetime
from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, List

from transliterate import translit

from const import VIDEO_PATH, DATE_FORMAT
from video import count_images, VideoRecorder
from database import db


app = FastAPI()

Path(VIDEO_PATH).mkdir(exist_ok=True)


class VideoRecorderInput(BaseModel):
    name: str
    comment: str
    rtsp_url: str
    fpm: int
    intervals: List[Dict[str, datetime]]


@app.post('/')
async def record(video_params: VideoRecorderInput):
    name, comment, rtsp_url, fpm, intervals = video_params.dict().values()

    if not rtsp_url.startswith('rtsp://'):
        return {
            'error': True,
            'description': f'RTSP url must start with "rtsp://"! Got {rtsp_url}.'
        }

    name = translit(name, 'ru', reversed=True)

    video_path = f'{VIDEO_PATH}/{name}'

    # if os.path.exists(video_path):
    #     return {
    #         'error': True,
    #         'description': f'The name {name} has already been occupied!'
    #     }
    Path(video_path).mkdir(exist_ok=True)

    for i, interval in enumerate(intervals):
        task_id = f'videos:{name}:{i}'

        rec = VideoRecorder(
            rtsp_string=rtsp_url,
            name=name,
            fpm=fpm,
            start_date=interval['date_from'],
            end_date=interval['date_to'],
            db_key=task_id,
        )

        image_number = rec.calculate_workload()

        db[task_id] = {
            "comment": comment,
            "rtsp_url": rtsp_url,
            "date_from": interval['date_from'].strftime(DATE_FORMAT),
            "date_to": interval['date_to'].strftime(DATE_FORMAT),
            "fpm": fpm,
            "image_number": image_number,
            "status": "queued",
        }
        rec.start()

    return {
        'error': False
    }


@app.get('/{name}')
async def get_progress(name):
    video_path = os.path.join(VIDEO_PATH, name)
    video_db_key = f'videos:{name}'

    if os.path.exists(video_path) and db[video_db_key]:
        return f'{count_images(video_path)}/' \
               f'{db[video_db_key]["image_number"]}'

    return 'No such task is currently running.'


if __name__ == "__main__":
    uvicorn.run('server:app', host="127.0.0.1", reload=True, port=8000)
