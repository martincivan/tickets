from typing import Optional
from datetime import datetime

from app.ticket_entries.models.ticket_data import TicketData, TicketType, TimeValidity, CurrentEntry


class TicketLoader:

    def __init__(self) -> None:
        self.tickets = {
            "ticketId1": {
                "ticket_type": TicketType.ONE_ENTRY.value,
                "entry_swimming_pool_id": None,
                "entry_at": None,
                "valid_from": datetime.fromtimestamp(0),
                "valid_until": datetime.fromtimestamp(2620335819),
                "remaining_uses": 1
            },
            "ticketId2": {
                "ticket_type": TicketType.TEN_ENTRIES.value,
                "entry_swimming_pool_id": "Pasienky",
                "entry_at": datetime.fromtimestamp(301),
                "valid_from": datetime.fromtimestamp(0),
                "valid_until": datetime.fromtimestamp(2620335819),
                "remaining_uses": 7
            },
            "ticketId3": {
                "ticket_type": TicketType.UNLIMITED.value,
                "entry_swimming_pool_id": None,
                "entry_at": None,
                "valid_from": datetime.fromtimestamp(0),
                "valid_until": datetime.fromtimestamp(2620335819),
                "remaining_uses": 0
            }
        }

    def load_ticket_data(self, ticket_id) -> Optional[TicketData]:
        if ticket_id in self.tickets:
            data = self.tickets[ticket_id]

            current_entry = None
            if data["entry_swimming_pool_id"] is not None and data["entry_at"] is not None:
                current_entry = CurrentEntry(swimming_pool_id=data["entry_swimming_pool_id"],
                                             at=data["entry_at"])
            return TicketData(ticket_id=ticket_id,
                              ticket_type=TicketType(data["ticket_type"]),
                              validity=TimeValidity(data["valid_from"], data["valid_until"], data["remaining_uses"]),
                              current_entry=current_entry)

    def exit_ticket(self, ticket_id: str):
        self.tickets[ticket_id]["entry_at"] = None
        self.tickets[ticket_id]["entry_swimming_pool_id"] = None

    def enter_ticket(self, ticket_id: str, swimming_pool_id: str, at: datetime, remaining_uses: int):
        self.tickets[ticket_id]["entry_at"] = at
        self.tickets[ticket_id]["entry_swimming_pool_id"] = swimming_pool_id
        self.tickets[ticket_id]["remaining_uses"] = remaining_uses

    def reenter_ticket(self, ticket_id: str, swimming_pool_id: str, at: datetime):
        self.tickets[ticket_id]["entry_at"] = at
        self.tickets[ticket_id]["entry_swimming_pool_id"] = swimming_pool_id
