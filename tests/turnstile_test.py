from unittest import IsolatedAsyncioTestCase

from app.ticket_entries.persistence.entry_loader import EntryLoader
from app.ticket_entries.persistence.ticket_loader import TicketLoader
from app.ticket_entries.ticket_provider import TicketValidityRepository
from app.ticket_entries.turnstile import Turnstile, Response


def get_turnstile() -> Turnstile:
    repo = TicketValidityRepository(TicketLoader(), EntryLoader())
    return Turnstile(ticket_provider=repo)


class TurnstileTest(IsolatedAsyncioTestCase):

    async def test_ok(self):
        turnstile = get_turnstile()
        self.assertEqual(Response.OK, (await turnstile.enter_ticket("ticketId1", "ZlatePiesky"))[0])
        self.assertEqual(Response.TICKET_INSIDE, (await turnstile.enter_ticket("ticketId1", "ZlatePiesky"))[0])
        self.assertEqual(Response.OK, (await turnstile.exit_ticket("ticketId1", "ZlatePiesky"))[0])
        self.assertEqual(Response.TICKET_CONSUMED, (await turnstile.enter_ticket("ticketId1", "Pasienky"))[0])
        self.assertEqual(Response.OK_REENTER, (await turnstile.enter_ticket("ticketId1", "ZlatePiesky"))[0])

    async def test_not_found(self):
        turnstile = get_turnstile()
        self.assertEqual(Response.TICKET_NOT_FOUND, (await turnstile.enter_ticket("not_existing", "ZlatePiesky"))[0])
        self.assertIsNone((await turnstile.enter_ticket("not_existing", "ZlatePiesky"))[1])
