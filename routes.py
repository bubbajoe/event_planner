import aiojobs

from mailer import event_invitation, event_signup
from database import Event, EventInviteRelation
from aiohttp import web
from datetime import datetime
from util import email_check, schema


event_schema = {
    'starts_at': {
        'type': 'datetime',
        'required': True,
        'coerce': (int, datetime.fromtimestamp),
    },
    'ends_at': {
        'type': 'datetime',
        'required': True,
        'coerce': (int, datetime.fromtimestamp),
    },
    'name': {
        'type': 'string',
        'minlength': 5,
        'required': False
    },
    'location': {
        'type': 'string',
        'minlength': 5,
        'required': True
    },
    'host_email': {
        'type': 'string',
        'required': True,
        'check_with': email_check
    },
    'invites': {
        'type': 'list',
        'required': False,
        'schema': {
            'type': 'dict',
            'required': True,
            'schema': {
                'name': {
                    'type': 'string',
                    'minlength': 3,
                    'required': True
                },
                'email': {
                    'type': 'string',
                    'required': True,
                    'check_with': email_check
                }
            }
        }
    }
}

@schema(event_schema)
async def post_event(request: web.Request, data={}):
    with request.app['db_session']() as session:
        event = Event(data['name'], data['location'], data['host_email'], data['starts_at'], data['ends_at'])
        session.add(event)
        session.flush()

        for invite in data['invites']:
            session.add(EventInviteRelation(event.uuid,
                invite['email'], invite['name']))
        session.flush()

        event_map = event.to_dict()
        await request.app['scheduler'].spawn(event_invitation(event_map, data['invites']))
        await request.app['scheduler'].spawn(event_signup(event_map, data['host_email']))
        return web.json_response(event_map)

async def get_events(request: web.Request):
    with request.app['db_session']() as session:
        events = session.query(Event).all()
        a = list(map(lambda e: e.to_dict(), events))
        return web.json_response(a)

async def delete_event(request: web.Request):
    event_uuid = request.match_info['event_uuid']
    with request.app['db_session']() as session:
        
        events = session.query(EventInviteRelation).filter(
            EventInviteRelation.email == request.json()['email'],
            EventInviteRelation.uuid == event_uuid).delete()
        a = list(map(lambda e: e.to_dict(), events))
        return web.json_response(a)
