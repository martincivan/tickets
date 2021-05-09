from datetime import datetime
from enum import Enum
from typing import Optional


class TimeValidity:

    def __init__(self, valid_from: datetime, valid_until: datetime, remaining_uses: int) -> None:
        super().__init__()
        if valid_from > valid_until:
            raise ValueError("valid_from is greater that valid_until")
        self.valid_until = valid_until
        self.valid_from = valid_from
        if remaining_uses < 0:
            raise ValueError("remaining uses cannot be negative")
        self.remaining_uses = remaining_uses


class CurrentEntry:

    def __init__(self, swimming_pool_id: str, at: datetime) -> None:
        super().__init__()
        self.swimming_pool_id = swimming_pool_id
        self.at = at


class TicketType(Enum):
    ONE_ENTRY = 1
    TEN_ENTRIES = 10
    UNLIMITED = 0


class TicketData:

    def __init__(self,
                 ticket_id: str,
                 ticket_type: TicketType,
                 validity: TimeValidity,
                 current_entry: Optional[CurrentEntry]):
        self.ticket_id: str = ticket_id
        self.ticket_type: TicketType = ticket_type
        self.validity: TimeValidity = validity
        self.current_entry: Optional[CurrentEntry] = current_entry
