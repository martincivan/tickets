import sys
from typing import Optional

from fastapi import FastAPI, Depends, Response
from fastapi.responses import JSONResponse
from dependency_injector import containers, providers
from dependency_injector.wiring import inject, Provide

from app.api import create_status_docs
from app.api.models import EntryAttempt, EntryAttemptResponse, TicketType
from app.ticket_entries.aggregates.ticket_validity import TicketValidity
from app.ticket_entries.persistence.entry_loader import EntryLoader
from app.ticket_entries.persistence.ticket_loader import TicketLoader
from app.ticket_entries.models.ticket_data import TicketType as AppTicketType
from app.ticket_entries.ticket_provider import TicketValidityRepository
from app.ticket_entries.turnstile import Turnstile, Response as AppResponse
import uvicorn


class Container(containers.DeclarativeContainer):
    ticket_loader = providers.Singleton(TicketLoader)
    entry_loader = providers.Singleton(EntryLoader)
    ticket_validity_repository = providers.Factory(TicketValidityRepository, ticket_loader=ticket_loader,
                                                   entry_loader=entry_loader)
    turnstile = providers.Factory(Turnstile, ticket_provider=ticket_validity_repository)


app = FastAPI()

response_map = {
    AppResponse.OK: {"code": 200, "description": "OK"},
    AppResponse.OK_REENTER: {"code": 201, "description": "Ticket re-entered"},
    AppResponse.TICKET_NOT_FOUND: {"code": 404, "description": "Ticket not found", "model": None},
    AppResponse.TICKET_CONSUMED: {"code": 402, "description": "Ticket is already consumed"},
    AppResponse.TICKET_INSIDE: {"code": 409, "description": "Ticket already inside / ticket not inside"},
    AppResponse.TICKET_NOT_INSIDE: {"code": 409, "description": "Ticket already inside / ticket not inside"},
    AppResponse.TICKET_TIME_EXPIRED: {"code": 423, "description": "Ticket expired"},
    AppResponse.TICKET_TIME_NOT_STARTED: {"code": 425, "description": "Ticket not available yet"},
}

ticket_type_map = {
    AppTicketType.ONE_ENTRY: TicketType.ONE_ENTRY,
    AppTicketType.TEN_ENTRIES: TicketType.TEN_ENTRIES,
    AppTicketType.UNLIMITED: TicketType.UNLIMITED,
}


@app.post("/entry", responses=create_status_docs(response_map=response_map, model=EntryAttemptResponse))
@inject
async def root(entry: EntryAttempt, turnstile: Turnstile = Depends(Provide[Container.turnstile])):
    app_response, ticket_validity = await turnstile.enter_ticket(ticket_id=entry.ticket_id,
                                                                 swimming_pool_id=entry.swimming_pool_id)

    return prepare_response(app_response=app_response, ticket_validity=ticket_validity)


@app.post("/exit", responses=create_status_docs(response_map=response_map, model=EntryAttemptResponse))
@inject
async def root(entry: EntryAttempt, turnstile: Turnstile = Depends(Provide[Container.turnstile])):
    app_response, ticket_validity = await turnstile.exit_ticket(ticket_id=entry.ticket_id,
                                                                swimming_pool_id=entry.swimming_pool_id)

    return prepare_response(app_response=app_response, ticket_validity=ticket_validity)


def prepare_response(app_response: AppResponse,
                     ticket_validity: Optional[TicketValidity]) -> Response:
    if ticket_validity is not None:
        body = {
            "remaining_entries": ticket_validity.remaining_entries,
            "valid_from": str(ticket_validity.valid_from),
            "valid_to": str(ticket_validity.valid_until),
            "current_entry_pool_id": ticket_validity.current_entry.swimming_pool_id if ticket_validity.current_entry else None,
            "current_entry_time": str(ticket_validity.current_entry.at) if ticket_validity.current_entry else None,
            "ticket_type": ticket_type_map[ticket_validity.ticket_type].value
        }
    else:
        body = {}
    return JSONResponse(status_code=response_map[app_response]["code"], content=body)


container = Container()
container.wire(modules=[sys.modules[__name__]])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
