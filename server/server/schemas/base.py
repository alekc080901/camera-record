from pydantic import BaseModel, validator, constr, PositiveFloat, PositiveInt
from abc import ABC

from server.const import DEFAULT_SEGMENT_TIME


class Config(BaseModel):
    audio: bool = False
    segment_time: PositiveInt = DEFAULT_SEGMENT_TIME


class BaseRecord(ABC, BaseModel):
    path: constr(max_length=100)
    name: constr(max_length=100)
    comment: constr(max_length=500)
    rtsp_url: constr(max_length=200)
    fpm: PositiveFloat = None

    config: Config

    @validator('name')
    def name_must_not_be_empty(cls, name):
        trash_symbols = ('\t', '\n', '\v', '\f', ' ')
        if all(s in trash_symbols for s in name):
            raise ValueError('Name must not be empty or contain only insignificant symbols!')
        return name

    @validator("path")
    def correct_path(cls, path):
        return path.strip('/\\')

    # @validator("config")
    # def config_values(cls, config):
    #     options = {'audio'}
    #
    #     if any(key not in options for key in config.keys()):
    #         raise ValueError('Wrong configuration options!')
    #
    #     for unmatched_option in options - set(config.keys()):
    #         config[unmatched_option] = False
    #
    #     return config
