from typing import Dict, List
from pydantic import validator

from datetime import time

from server.server.schemas.base import BaseRecord


class RegularVideoRecorderInput(BaseRecord):

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

    @validator("days_of_week")
    def days_in_interval(cls, days_of_week):
        if any(day not in range(0, 7) for day in days_of_week):
            raise ValueError("Days of week must be in range of 0..6!")
        return days_of_week
