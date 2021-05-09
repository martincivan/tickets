from datetime import datetime
from typing import Optional

from app.ticket_entries.aggregates.event import TicketLeft, TicketEntered, TicketReentered
from app.ticket_entries.persistence.entry_loader import EntryLoader
from app.ticket_entries.persistence.ticket_loader import TicketLoader
from app.ticket_entries.aggregates.ticket_validity import TicketValidity


class TicketValidityRepository:

    def __init__(self, ticket_loader: TicketLoader, entry_loader: EntryLoader):
        self.ticket_loader: TicketLoader = ticket_loader
        self.entry_loader: EntryLoader = entry_loader
        self.actions: dict = {
            TicketLeft: self.ticket_left,
            TicketEntered: self.ticket_entered,
            TicketReentered: self.ticket_reentered,
        }

    def get_ticket_validity(self, ticket_id: str, entries_from: datetime, entries_until: datetime, entry_swimming_pool_id: str) -> Optional[TicketValidity]:
        ticket_data = self.ticket_loader.load_ticket_data(ticket_id)
        if ticket_data is None:
            return None
        ticket_entries = self.entry_loader.load_entries(ticket_id, entries_from, entries_until, entry_swimming_pool_id)
        return TicketValidity(ticket_data=ticket_data, valid_entries=ticket_entries)

    def save(self, ticket_validity: TicketValidity):
        event = ticket_validity.event
        self.actions[type(event)](event)

    def ticket_left(self, event: TicketLeft):
        self.ticket_loader.exit_ticket(event.ticket_id)
        self.entry_loader.end_entry(ticket_id=event.ticket_id, entry_swimming_pool_id=event.swimming_pool_id, at=event.left_at)

    def ticket_entered(self, event: TicketEntered):
        self.ticket_loader.enter_ticket(event.ticket_id, event.swimming_pool_id, event.entered_at, event.remaining_uses)
        self.entry_loader.start_entry(ticket_id=event.ticket_id, entry_swimming_pool_id=event.swimming_pool_id, at=event.entered_at)

    def ticket_reentered(self, event: TicketReentered):
        self.ticket_loader.reenter_ticket(event.ticket_id, event.swimming_pool_id, event.entered_at)
        self.entry_loader.start_entry(ticket_id=event.ticket_id, entry_swimming_pool_id=event.swimming_pool_id, at=event.entered_at)

