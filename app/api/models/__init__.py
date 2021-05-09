from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class EntryAttempt(BaseModel):
    ticket_id: str
    swimming_pool_id: str


class TicketType(Enum):
    ONE_ENTRY = "single_entry"
    TEN_ENTRIES = "ten_entries"
    UNLIMITED = "unlimited_entries"


class EntryAttemptResponse(BaseModel):
    remaining_entries: int
    valid_from: datetime
    valid_to: datetime
    current_entry_pool_id: str
    current_entry_time: datetime
    ticket_type: TicketType
