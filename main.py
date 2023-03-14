import uvicorn

from src.database import RedisConnection
from src.disk_uploader.disk_process import DiskConnection
from const import REDIS_SERVER, REDIS_PORT, REDIS_DB, CLOUD_ACCESS_TOKEN
from src.video_recorder.regular_record_timer import RegularRecording


def main():
    redis_db = RedisConnection(REDIS_SERVER, REDIS_PORT, REDIS_DB)

    yandex_disk = DiskConnection(token=CLOUD_ACCESS_TOKEN)
    redis_db.drop_statuses()

    regular_recorder = RegularRecording()

    regular_recorder.start()
    yandex_disk.start()

    uvicorn.run('server:app', host="127.0.0.1", reload=True, port=8888)


if __name__ == "__main__":
    main()
