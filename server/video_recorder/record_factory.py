from server.video_recorder.video_audio_record_process import VideoAudioRecorder
from server.video_recorder.record_process import VideoRecorder


def create_recorder(audio: bool, **kwargs):
    if audio:
        kwargs.pop('fpm', None)

    return VideoAudioRecorder(**kwargs) if audio else VideoRecorder(**kwargs)
