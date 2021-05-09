from datetime import datetime
from unittest import TestCase

from app.ticket_entries.aggregates.ticket_validity import TicketValidity
from app.ticket_entries.models.ticket_data import TicketData, TicketType, TimeValidity


class TicketValidityTest(TestCase):

    def test_one_entry(self):
        time_validity = TimeValidity(valid_from=datetime.fromtimestamp(50), valid_until=datetime.fromtimestamp(150),
                                     remaining_uses=1)
        ticket_data = TicketData(ticket_id="ticket_id", ticket_type=TicketType.ONE_ENTRY, validity=time_validity,
                                 current_entry=None)
        validity = TicketValidity(ticket_data, [])

        enter_time1 = datetime.fromtimestamp(100)
        enter_time2 = datetime.fromtimestamp(120)

        self.assertFalse(validity.exit())
        self.assertFalse(validity.re_enter("ZlatePiesky", enter_time2))
        self.assertTrue(validity.enter("ZlatePiesky", enter_time1))
        self.assertEqual(0, validity.remaining_entries)
        self.assertIsNotNone(validity.current_entry)
        self.assertEqual("ZlatePiesky", validity.current_entry.swimming_pool_id)
        self.assertEqual(enter_time1, validity.current_entry.at)
        self.assertFalse(validity.enter("ZlatePiesky", enter_time1))
        self.assertFalse(validity.enter("Pasienky", enter_time1))
        self.assertEqual(enter_time1, validity.current_entry.at)
        self.assertTrue(validity.exit())
        self.assertFalse(validity.enter("Pasienky", enter_time2))
        self.assertFalse(validity.enter("ZlatePiesky", enter_time2))
        self.assertFalse(validity.re_enter("Pasienky", enter_time2))
        self.assertTrue(validity.re_enter("ZlatePiesky", enter_time2))

    def test_unlimited_entries(self):
        time_validity = TimeValidity(valid_from=datetime.fromtimestamp(50), valid_until=datetime.fromtimestamp(150),
                                     remaining_uses=0)
        ticket_data = TicketData(ticket_id="ticket_id", ticket_type=TicketType.UNLIMITED, validity=time_validity,
                                 current_entry=None)
        validity = TicketValidity(ticket_data, [])
        enter_time1 = datetime.fromtimestamp(100)
        enter_time2 = datetime.fromtimestamp(120)
        self.assertTrue(validity.enter("ZlatePiesky", enter_time1))
        self.assertEqual(0, validity.remaining_entries)
        self.assertFalse(validity.re_enter("ZlatePiesky", enter_time2))
        self.assertFalse(validity.enter("ZlatePiesky", enter_time2))
        self.assertFalse(validity.enter("Pasienky", enter_time2))
        self.assertTrue(validity.exit())
        self.assertTrue(validity.enter("Pasienky", enter_time2))
        self.assertEqual(0, validity.remaining_entries)
        self.assertFalse(validity.enter("ZlatePiesky", enter_time2))

    def test_two_pools_multiple_entries(self):
        time_validity = TimeValidity(valid_from=datetime.fromtimestamp(50), valid_until=datetime.fromtimestamp(150),
                                         remaining_uses=3)
        ticket_data = TicketData(ticket_id="ticket_id", ticket_type=TicketType.ONE_ENTRY, validity=time_validity,
                                 current_entry=None)
        validity = TicketValidity(ticket_data, [])

        enter_time1 = datetime.fromtimestamp(100)
        enter_time2 = datetime.fromtimestamp(110)
        enter_time3 = datetime.fromtimestamp(120)
        enter_time4 = datetime.fromtimestamp(130)

        self.assertTrue(validity.enter("ZlatePiesky", enter_time1))
        self.assertEqual(2, validity.remaining_entries)
        self.assertIsNotNone(validity.current_entry)
        self.assertEqual("ZlatePiesky", validity.current_entry.swimming_pool_id)
        self.assertEqual(enter_time1, validity.current_entry.at)

        self.assertTrue(validity.exit())

        self.assertFalse(validity.re_enter("Pasienky", enter_time2))
        self.assertTrue(validity.enter("Pasienky", enter_time2))
        self.assertEqual(1, validity.remaining_entries)
        self.assertEqual(enter_time2, validity.current_entry.at)
        self.assertEqual("Pasienky", validity.current_entry.swimming_pool_id)

        self.assertTrue(validity.exit())

        self.assertTrue(validity.re_enter("Pasienky", enter_time3))
        self.assertEqual(1, validity.remaining_entries)
        self.assertEqual(enter_time3, validity.current_entry.at)
        self.assertEqual("Pasienky", validity.current_entry.swimming_pool_id)

        self.assertTrue(validity.exit())

        self.assertTrue(validity.re_enter("ZlatePiesky", enter_time4))
        self.assertEqual(1, validity.remaining_entries)
