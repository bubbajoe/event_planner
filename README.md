# Event Planner Service


# Starting the Application?

Python 3.8 Recommended!

1. Edit the `config.yml` and add your gmail login credentials automated

1. Install dependencies

`pip3 install -r requirements.txt`

1. Create database and add test events (specified in `events.json`)

`python3 database.py`

1. Run server

`python3 server.py`

# REST API Docs

### Get all events
GET /api/event

### Create event
POST /api/event
```
{
    "name": "Interview w/ Client",
    "location": "Google Hangouts (meet.google.com/...)",
    "host_email": "pma@company.com",
    "starts_at": 1599559200,
    "ends_at": 1599559200,
    "invites": [
        {
            "email": "leaddev@company.com",
            "name": "Lead Developer @ Company"
        },
        {
            "email": "pm@client.com",
            "name": "Project Manager @ Client Company"
        }
    ]
}
```

### Delete event
DELETE /api/event
{
    "event_uuid": "60fddcef-aa2c-428d-b1a4-3c713537f014"
}