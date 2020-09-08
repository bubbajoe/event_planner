import re
import cerberus
import aiojobs
from sqlalchemy.exc import IntegrityError
from aiohttp import web
from aiohttp_swagger3 import SwaggerDocs, SwaggerUiSettings
from database import Event, EventInviteRelation, session_ctx
from routes import *
from datetime import datetime
from util import email_check, schema, Config
from routes import event_schema, get_events, delete_event



async def setup_instances(app):
    app['config'] = Config()
    app['db_session'] = session_ctx
    app['scheduler'] = await aiojobs.create_scheduler()

@web.middleware
async def error_handler(request, handler):
    try:
        return await handler(request)
    except IntegrityError as e:
        return web.json_response(
            {'error': 'duplicate email'}, status=422)
    except web.HTTPException as e:
        return web.json_response(
            {'error': e.reason}, status=e.status_code)
    except Exception as e:
        return web.json_response(
            {'error': 'Unexpected error occured'}, status=500)

app = web.Application(middlewares=[error_handler])
app.on_startup.append(setup_instances)

swagger = SwaggerDocs(
    app, title="Event Manager API", version="1.0.0",
    swagger_ui_settings=SwaggerUiSettings(path="/api/docs")
)

swagger.add_routes([
    # List all events
    web.get("/api/event", get_events),

    # Create events
    web.post("/api/event", post_event),

    web.delete("/api/event", delete_event)

    # Not Setup: Reply to an event (accept, decline, etc...)
    # web.post("/api/event/{event_uuid}/{status}", None),

])

web.run_app(app)