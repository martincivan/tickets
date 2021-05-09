from datetime import datetime
from typing import Optional

from app.ticket_entries.aggregates import EventAggregate
from app.ticket_entries.aggregates.event import TicketLeft, TicketReentered, TicketEntered
from app.ticket_entries.models.entry import Entry
from app.ticket_entries.models.ticket_data import TicketData, CurrentEntry, TicketType


class TicketValidity(EventAggregate):
    def __init__(self, ticket_data: TicketData, valid_entries: list[Entry]):
        super().__init__()
        self._ticket_data: TicketData = ticket_data
        self._valid_entries: list[Entry] = valid_entries

    @property
    def current_entry(self) -> Optional[CurrentEntry]:
        return self._ticket_data.current_entry

    @property
    def valid_entries(self) -> tuple[Entry]:
        return tuple(self._valid_entries)

    @property
    def valid_from(self) -> datetime:
        return self._ticket_data.validity.valid_from

    @property
    def valid_until(self) -> datetime:
        return self._ticket_data.validity.valid_until

    @property
    def remaining_entries(self) -> int:
        return self._ticket_data.validity.remaining_uses

    @property
    def ticket_type(self) -> TicketType:
        return self._ticket_data.ticket_type

    def exit(self) -> bool:
        if self.current_entry is None:
            return False

        finished = datetime.now()
        for entry in self._valid_entries:
            if entry.swimming_pool_id == self.current_entry.swimming_pool_id and entry.finished is None:
                entry.finished = finished
        self._event = TicketLeft(ticket_id=self._ticket_data.ticket_id,
                                 swimming_pool_id=self.current_entry.swimming_pool_id,
                                 left_at=finished)
        self._ticket_data.current_entry = None
        return True

    def re_enter(self, swimming_pool_id: str, at: datetime) -> bool:
        if self.current_entry is not None:
            return False
        today = at.date()
        today_datetime = datetime(today.year, today.month, today.day)
        tomorrow_datetime = datetime(today.year, today.month, today.day + 1)
        for entry in self._valid_entries:
            if entry.swimming_pool_id == swimming_pool_id and today_datetime < entry.started < tomorrow_datetime:
                self._event = TicketReentered(ticket_id=self._ticket_data.ticket_id,
                                              swimming_pool_id=swimming_pool_id,
                                              entered_at=at,
                                              remaining_uses=self._ticket_data.validity.remaining_uses)
                self._ticket_data.current_entry = CurrentEntry(swimming_pool_id=swimming_pool_id, at=at)
                self._valid_entries.append(Entry(swimming_pool_id=swimming_pool_id, started=at))
                return True
        return False

    def enter(self, swimming_pool_id: str, at: datetime):
        if self.current_entry is not None:
            return False
        if self._ticket_data.ticket_type == TicketType.UNLIMITED:
            self._perform_enter(at=at, swimming_pool_id=swimming_pool_id)
            return True
        if self._ticket_data.validity.remaining_uses > 0:
            self._ticket_data.validity.remaining_uses -= 1
            self._perform_enter(at=at, swimming_pool_id=swimming_pool_id)
            return True
        return False

    def _perform_enter(self, at, swimming_pool_id):
        self._event = TicketEntered(ticket_id=self._ticket_data.ticket_id,
                                    swimming_pool_id=swimming_pool_id,
                                    entered_at=at,
                                    remaining_uses=self._ticket_data.validity.remaining_uses)
        self._ticket_data.current_entry = CurrentEntry(swimming_pool_id=swimming_pool_id, at=at)
        self._valid_entries.append(Entry(swimming_pool_id=swimming_pool_id, started=at))
