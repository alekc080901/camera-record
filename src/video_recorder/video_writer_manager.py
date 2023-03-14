import cv2

import directory_methods


class VideoWriterManager:
    _writers = {}

    def __new__(cls, *args, **kwargs):
        if kwargs['writer_path'] not in cls._writers:
            cls._writers['writer_path'] = super().__new__(cls)
        return cls._writers['writer_path']

    @staticmethod
    def _extract_images_from_video(video_path: str):
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

        return video_info, images

    @staticmethod
    def _get_video_writer_from_existing_video(video_path, codec):
        info, images = VideoWriterManager._extract_images_from_video(video_path)

        new_path = directory_methods.create_copy_of_filename(video_path)
        resolution, fps = info

        writer = cv2.VideoWriter(
            new_path,
            codec,
            fps,
            resolution,
        )

        for im in images:
            writer.write(im)

        return writer

    def __init__(self, *, writer_path, codec, fps, resolution):
        self._path = writer_path

        if directory_methods.exists(writer_path):
            self._copy = True
            self._writer = VideoWriterManager._get_video_writer_from_existing_video(writer_path, codec)
        else:
            self._copy = False
            self._writer = cv2.VideoWriter(
                writer_path,
                codec,
                fps,
                resolution,
            )

    @classmethod
    def _remove_writer(cls, writer_path):
        if writer_path in cls._writers:
            del cls._writers[writer_path]

    def write(self, image):
        self._writer.write(image)

    def release(self):
        self._writer.release()

        if self._copy:
            old_path = directory_methods.create_copy_of_filename(self._path)
            directory_methods.rename(old_path, self._path)

        VideoWriterManager._remove_writer(self._path)
