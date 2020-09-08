import json

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, Session, relationship

from util import hash_password, Config
from uuid import uuid4
from datetime import datetime
from hashlib import sha256
from contextlib import contextmanager

conf = Config()
DB_URI = conf.get('database_settings', 'uri')

# Get the database session
def _get_session(**kwargs) -> Session:
    return sessionmaker(bind=create_engine(DB_URI))(**kwargs)

# Get a transactional database session via the context manager
@contextmanager
def session_ctx(**kwargs):
    session = _get_session(**kwargs)
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

Base = declarative_base()

# Event
class Event(Base):
    __tablename__ = 'events'
    uuid = Column(String(36), primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    location = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    starts_at = Column(DateTime, nullable=False)
    ends_at = Column(DateTime, nullable=False)

    invites = relationship("EventInviteRelation",
        primaryjoin="Event.uuid==EventInviteRelation.uuid")

    def __init__(self, name, location, email, starts_at, ends_at):
        self.uuid = str(uuid4())
        self.name = name
        self.location = location
        self.email = email
        self.starts_at = starts_at
        self.ends_at = ends_at

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    def to_dict(self, keys=None, invite_keys=['email', 'name', 'status']):
        to_serialize = keys or [
            'uuid', 'name', 'location',
            'created_at', 'starts_at',
            'ends_at', 'invites',
        ]
        d = {}
        for attr in to_serialize:
            o = getattr(self, attr)
            # For created_at, starts_at, and ends_at
            if type(o) == datetime:
                o = o.isoformat()
            # For invites
            if attr == 'invites':
                o = list(map(lambda e: e.to_dict(invite_keys), o))
            d[attr] = o
        return d

# EventInviteRelation - holds the events
class EventInviteRelation(Base):
    __tablename__ = 'event_invite_relation'
    uuid = Column(String(36), ForeignKey("events.uuid"), primary_key=True, nullable=False)
    email = Column(String, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    status = Column(String, default='?')
    invited_at = Column(DateTime, default=func.now(), nullable=False)

    def __init__(self, uuid, email, name, status=None):
        self.uuid = uuid
        self.name = name
        self.email = email
        self.status = status

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    def to_dict(self, keys=None):
        to_serialize = keys or [
            'uuid', 'name', 'email',
            'status', 'creator', 'invited_at'
        ]
        d = {}
        for attr in to_serialize:
            d[attr] = getattr(self, attr)
        return d

# open events file
def open_events_file(filename="events.json"):
    with open(filename) as json_file:
        data = json.load(json_file)
        return data


# creates database and example data
if __name__ == "__main__":
    engine = create_engine(DB_URI)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    events = open_events_file()
    for event_data in events:
        with session_ctx() as sess:
            # Create test event
            interview = Event(event_data['name'],
                event_data['location'], event_data['host_email'],
                datetime.fromtimestamp(event_data['starts_at']),
                datetime.fromtimestamp(event_data['ends_at']))
            # Add Event row
            sess.add(interview)
            # Flush row to the database to get the uuid
            sess.flush()

            # Add invite emails to the event
            for invite in event_data['invites']:
                event_invite = EventInviteRelation(
                    interview.uuid, invite['email'], invite['name'],)
                sess.add(event_invite)
            sess.flush()
            print(interview.to_dict())
    print("Test data was successfully added")