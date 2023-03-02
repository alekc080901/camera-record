import uvicorn

from datetime import datetime

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class VideoRecorderInput(BaseModel):
    name: str
    comment: str
    rtsp_route: str
    date_from: datetime
    date_to: datetime
    fpm: int


@app.post("/")
async def root(record_params: VideoRecorderInput):
    return {
        'date': (record_params.date_from, record_params.date_to)
    }


if __name__ == "__main__":
    uvicorn.run('main:app', host="127.0.0.1", reload=True, port=8000)
