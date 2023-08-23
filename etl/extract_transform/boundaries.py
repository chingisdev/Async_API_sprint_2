import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, Union


@dataclass
class DateBoundaries:
    from_time: datetime
    step: timedelta

    @property
    def till_time(
        self,
    ) -> datetime:
        return self.from_time + self.step

    def __repr__(
        self,
    ):
        return f"from {self.from_time.isoformat()} : till {self.till_time.isoformat()}"


def get_query_boundaries(
    last_update_time: Optional[
        Union[
            datetime,
            str,
        ]
    ],
    time_delta=None,
) -> Optional[DateBoundaries]:
    if not last_update_time:
        return None
    if not time_delta:
        time_delta = timedelta(minutes=1)
    if isinstance(
        last_update_time,
        str,
    ):
        last_update_time = datetime.fromisoformat(last_update_time)
    date_boundaries = DateBoundaries(
        from_time=last_update_time,
        step=time_delta,
    )
    return date_boundaries
