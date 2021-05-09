class EventAggregate:

    def __init__(self) -> None:
        super().__init__()
        self._event = None

    @property
    def event(self):
        return self._event
