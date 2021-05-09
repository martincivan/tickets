from datetime import datetime

from app.ticket_entries.models.entry import Entry


def data_to_entry(data: dict) -> Entry:
    return Entry(**data)


class EntryLoader:

    def __init__(self) -> None:
        self.entries = {
            "ticketId2": [
                {
                    "swimming_pool_id": "ZlatePiesky",
                    "started": datetime.fromtimestamp(0),
                    "finished": datetime.fromtimestamp(100)
                },
                {
                    "swimming_pool_id": "Lamac",
                    "started": datetime.fromtimestamp(200),
                    "finished": datetime.fromtimestamp(300)
                },
                {
                    "swimming_pool_id": "Pasienky",
                    "started": datetime.fromtimestamp(301),
                    "finished": None
                }
            ]
        }

    def load_entries(self, ticket_id: str, entries_from: datetime, entries_until: datetime,
                     entry_swimming_pool_id: str) -> list[Entry]:
        if ticket_id not in self.entries:
            return []
        valid = filter(lambda data: entries_from <= data["started"] < entries_until,
                       self.entries[ticket_id])
        valid = filter(lambda data: data["swimming_pool_id"] == entry_swimming_pool_id, valid)
        return list(map(data_to_entry, valid))

    def end_entry(self, ticket_id: str, entry_swimming_pool_id: str, at: datetime):
        for entry in self.entries[ticket_id]:
            if entry["swimming_pool_id"] == entry_swimming_pool_id:
                entry["finished"] = at

    def start_entry(self, ticket_id: str, entry_swimming_pool_id: str, at: datetime):
        if ticket_id not in self.entries:
            self.entries[ticket_id] = []
        self.entries[ticket_id].append({
            "swimming_pool_id": entry_swimming_pool_id,
            "started": at,
            "finished": None
        })
