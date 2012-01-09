from pyramid.renderers import get_renderer

from pyramid.events import subscriber
from pyramid.events import BeforeRender

from pyramid.security import authenticated_userid

@subscriber(BeforeRender)
def add_base_template(event):
    layout = get_renderer('templates/layout.pt').implementation()
    event.update({'layout': layout})

@subscriber(BeforeRender)
def add_login_status(event):
    event.update({'authenticated_userid': authenticated_userid(event['request'])})
