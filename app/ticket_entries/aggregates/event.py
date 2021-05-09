from datetime import datetime


class TicketLeft:

    def __init__(self, ticket_id: str, swimming_pool_id: str, left_at: datetime) -> None:
        self.swimming_pool_id = swimming_pool_id
        self.ticket_id = ticket_id
        self.left_at = left_at


class TicketEntered:

    def __init__(self, ticket_id: str, swimming_pool_id: str, entered_at: datetime, remaining_uses: int):
        self.remaining_uses = remaining_uses
        self.swimming_pool_id = swimming_pool_id
        self.ticket_id = ticket_id
        self.entered_at = entered_at


class TicketReentered:

    def __init__(self, ticket_id: str, swimming_pool_id: str, entered_at: datetime, remaining_uses: int):
        self.remaining_uses = remaining_uses
        self.swimming_pool_id = swimming_pool_id
        self.ticket_id = ticket_id
        self.entered_at = entered_at
