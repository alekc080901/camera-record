import uvicorn

from server.database import RedisConnection
from server.disk_uploader.disk_process import DiskConnection
from server.const import REDIS_SERVER, REDIS_PORT, REDIS_DB, CLOUD_ACCESS_TOKEN
from server.video_recorder.record_launcher import RecordManager


def main():
    redis_db = RedisConnection(REDIS_SERVER, REDIS_PORT, REDIS_DB)

    yandex_disk = DiskConnection(token=CLOUD_ACCESS_TOKEN)
    # redis_db.reset_tasks()

    recorder = RecordManager()

    recorder.start()
    yandex_disk.start()

    uvicorn.run('server.server.views:app', host="127.0.0.1", reload=False, port=8000)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Server stop")
