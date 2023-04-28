from server.video_recorder.video_audio_record_process import VideoAudioRecorder
from server.video_recorder.record_process import VideoRecorder


def create_recorder(audio: bool, **kwargs):
    """
    Функция по созданию объектов класса VideoAudioRecorder и VideoRecorder.
    :param audio: Создавать объект VideoAudioRecorder (True) или VideoRecorder (False)
    :param kwargs: Атрибуты класса
    :return: Объект класса записи
    """
    if audio:
        kwargs.pop('fpm', None)

    return VideoAudioRecorder(**kwargs) if audio else VideoRecorder(**kwargs)
