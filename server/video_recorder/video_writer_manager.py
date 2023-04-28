import cv2

import server.directory_methods as directory_methods
from server.const import VIDEO_CODEC


def extract_frames_from_video(video_path: str):
    """
    Считывает все кадры из видео.
    :param video_path: Путь до видео
    :return video_info: Информация о разрешении и fps камеры
    :return images: Список кадров из видео
    """
    vid = cv2.VideoCapture(video_path)
    images = []

    fps = vid.get(cv2.CAP_PROP_FPS)
    res = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH)), int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))

    video_info = (res, fps)

    while vid.isOpened():
        ret, frame = vid.read()
        if not ret:
            break

        images.append(frame)

    vid.release()
    return video_info, images


class VideoWriterManager:
    """
    Осуществляет запись кадров в файл (в данном случае из трансляции с камеры)
    :param writer_path: Путь до видео
    :param fps: FPS видеофайла
    :param resolution: Разрешение видеофайла

    :param self._copy: Находится ли по указанному пути видеофайл
    """

    @staticmethod
    def _get_video_writer_from_existing_video(video_path):
        """
        Возвращает объект VideoWriter из OpenCV, считывая изображения из видео
        :param video_path: Путь до существующего видео
        :return: Объект VideoWriter
        """
        info, images = extract_frames_from_video(video_path)

        new_path = directory_methods.create_copy_of_filename(video_path)
        resolution, fps = info

        writer = cv2.VideoWriter(
            new_path,
            *VIDEO_CODEC,
            fps,
            resolution,
        )

        for im in images:
            writer.write(im)

        return writer

    def __init__(self, *, writer_path: str, fps: int | float, resolution: tuple[int, int]):
        self._path = writer_path

        if directory_methods.exists(writer_path):
            self._copy = True
            self._writer = VideoWriterManager._get_video_writer_from_existing_video(writer_path)
        else:
            self._copy = False
            self._writer = cv2.VideoWriter(
                writer_path,
                cv2.VideoWriter_fourcc(*f'{VIDEO_CODEC}'),
                fps,
                resolution,
            )

    def write(self, image):
        """
        Запись изображения в видео.
        :param image: Изображение
        """
        self._writer.write(image)

    def release(self):
        """
        Прекращение процесса записи в файл.
        """
        self._writer.release()

        if self._copy:
            old_path = directory_methods.create_copy_of_filename(self._path)
            directory_methods.rename(old_path, self._path)
