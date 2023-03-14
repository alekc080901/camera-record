from typing import Dict, List
from src.server.schemas.record import VideoRecorderInput
from pydantic import BaseModel, validator, Field

from datetime import time


class RegularVideoRecorderInput(VideoRecorderInput):

    intervals: List[Dict[str, time]]
    days_of_week: List[int]

    @validator("intervals")
    def correct_intervals(cls, intervals):
        for interval in intervals:

            if len(interval.keys()) != 2:
                raise ValueError("Wrong number of keys in interval!")

            if 'time_from' not in interval or 'time_to' not in interval:
                raise ValueError("Some keys missing in interval!")

        return intervals
