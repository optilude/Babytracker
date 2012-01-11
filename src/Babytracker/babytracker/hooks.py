from pyramid.renderers import get_renderer

from pyramid.events import subscriber
from pyramid.events import BeforeRender
from pyramid.events import NewRequest

from pyramid.security import authenticated_userid

@subscriber(BeforeRender)
def add_base_template(event):
    layout = get_renderer('templates/layout.pt').implementation()
    event.update({'layout': layout})

@subscriber(BeforeRender)
def add_login_status(event):
    event.update({'authenticated_userid': authenticated_userid(event['request'])})

def api_access_control(request, response):
    """Set CORS Access-Control-* headers if the request itself did not for
    requests coming into on the /api route.

    By default, we allow all origins, credentials and the Content-Type header.
    """
    if request.matched_route is not None and request.matched_route.name == 'api':
        if 'Access-Control-Allow-Origin' not in response.headers:
            response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
        if 'Access-Control-Allow-Credentials' not in response.headers:
            response.headers['Access-Control-Allow-Credentials'] = 'true'
        if 'Access-Control-Allow-Headers' not in response.headers:
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type'

@subscriber(NewRequest)
def add_api_access_control(event):
    request = event.request
    request.add_response_callback(api_access_control)