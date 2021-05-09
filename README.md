# FastApi Demo

## Running with Python 3.9 in path:
- (optional) create venv using `python3 -m venv` and activate using `./venv/bin/activate`
- install requirements: `pip install -r requirements.txt`
- run `uvicorn app.main:app` (or alternatively `python -m app.main`)
- OpenAPI docs should be available at http://127.0.0.1/docs

Run tests using `python -m unittest discover -s . -p "*_test.py"`

## Running in Docker:
- build image using `docker build -t <image_name> .` - example: `docker build -t tickets .`
- run image in container: `docker run -d --name <container_name -p 80:80 <image_name>` - example: `docker run -d --name tickets -p 80:80 tickets`
- OpenAPI docs should be available at http://127.0.0.1/docs

Tickets can be created/modified in `app/ticket_entries_persistence_ticket_loader.py`, currently exists 3 tickets: 
- `ticketId1` - one entry ticket
- `ticketId2` - 10 entries ticket with 7 remaining entries and currently being used 
- `ticketId3` - no entry-limit ticket


