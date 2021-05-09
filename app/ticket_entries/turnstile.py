import logging
from enum import Enum
from typing import  Optional
from datetime import datetime

from app.ticket_entries.aggregates.ticket_validity import TicketValidity
from app.ticket_entries.ticket_provider import TicketValidityRepository


class Response(Enum):
    OK = 0
    OK_REENTER = -1
    TICKET_NOT_FOUND = 1
    TICKET_TIME_NOT_STARTED = 2
    TICKET_TIME_EXPIRED = 3
    TICKET_CONSUMED = 4
    TICKET_INSIDE = 5
    TICKET_NOT_INSIDE = 6


class Turnstile:

    def __init__(self, ticket_provider: TicketValidityRepository) -> None:
        self.ticket_repository: TicketValidityRepository = ticket_provider

    async def enter_ticket(self, ticket_id: str, swimming_pool_id: str) -> tuple[Response, Optional[TicketValidity]]:
        now = datetime.now()
        today = now.date()
        today_datetime = datetime(today.year, today.month, today.day)
        tomorrow_datetime = datetime(today.year, today.month, today.day + 1)
        ticket_validity = self.ticket_repository.get_ticket_validity(ticket_id=ticket_id,
                                                                     entry_swimming_pool_id=swimming_pool_id,
                                                                     entries_from=today_datetime,
                                                                     entries_until=tomorrow_datetime)
        if ticket_validity is None:
            return Response.TICKET_NOT_FOUND, None

        if ticket_validity.current_entry is not None:
            if ticket_validity.current_entry.at < today_datetime:
                logging.warning("Ticket %s inside more than 1 day, from: %s, exiting ticket.",
                                ticket_id,
                                ticket_validity.current_entry.at)
                if ticket_validity.exit():
                    self.ticket_repository.save(ticket_validity)
                    ticket_validity = self.ticket_repository.get_ticket_validity(ticket_id=ticket_id,
                                                                                 entry_swimming_pool_id=swimming_pool_id,
                                                                                 entries_from=today_datetime,
                                                                                 entries_until=tomorrow_datetime)
            else:
                return Response.TICKET_INSIDE, ticket_validity

        if ticket_validity.re_enter(swimming_pool_id=swimming_pool_id, at=now):
            self.ticket_repository.save(ticket_validity=ticket_validity)
            return Response.OK_REENTER, ticket_validity

        if ticket_validity.valid_from > now:
            return Response.TICKET_TIME_NOT_STARTED, ticket_validity

        if ticket_validity.valid_until < now:
            return Response.TICKET_TIME_EXPIRED, ticket_validity

        if ticket_validity.enter(swimming_pool_id=swimming_pool_id, at=now):
            self.ticket_repository.save(ticket_validity=ticket_validity)
            return Response.OK, ticket_validity
        return Response.TICKET_CONSUMED, ticket_validity

    async def exit_ticket(self, ticket_id: str, swimming_pool_id: str) -> tuple[Response, Optional[TicketValidity]]:
        now = datetime.now()
        today = now.date()
        today_datetime = datetime(today.year, today.month, today.day)
        tomorrow_datetime = datetime(today.year, today.month, today.day + 1)
        ticket_validity = self.ticket_repository.get_ticket_validity(ticket_id=ticket_id,
                                                                     entry_swimming_pool_id=swimming_pool_id,
                                                                     entries_from=today_datetime,
                                                                     entries_until=tomorrow_datetime)

        if ticket_validity is None:
            return Response.TICKET_NOT_FOUND, None

        if ticket_validity.current_entry is not None:
            if ticket_validity.exit():
                self.ticket_repository.save(ticket_validity)
                return Response.OK, ticket_validity
        return Response.TICKET_NOT_INSIDE, ticket_validity
