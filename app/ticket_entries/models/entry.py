from datetime import datetime
from typing import Optional


class Entry:
    def __init__(self, swimming_pool_id: str, started: datetime, finished: Optional[datetime] = None):
        self.swimming_pool_id = swimming_pool_id
        if finished and started > finished:
            raise ValueError("Entry started after being finished")
        self.started = started
        self.finished = finished

