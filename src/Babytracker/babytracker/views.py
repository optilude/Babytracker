from pyramid.view import view_config, view_defaults
from babytracker.interfaces import IMobileRequest
from babytracker.interfaces import IDesktopRequest

# Until https://github.com/Pylons/pyramid/issues/394 is released
# @view_defaults(request_type=IMobileRequest)
class MobileViews(object):

    def __init__(self, request):
        self.request = request

    @view_config(name='', request_type=IMobileRequest, renderer='templates/mobile_home.pt')
    def home(self):

        return {
        }

# Until https://github.com/Pylons/pyramid/issues/394 is released
# @view_defaults(request_type=IDesktopRequest)
class DesktopViews(object):

    def __init__(self, request):
        self.request = request

    @view_config(name='', request_type=IDesktopRequest, renderer='templates/home.pt')
    def home(self):

        return {
        }
