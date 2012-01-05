from pyramid.view import view_config

class MobileViews(object):

    def __init__(self, request):
        self.request = request

    @view_config(route_name='mobile_home', renderer='templates/mobile_home.pt')
    def home(self):

        return {
        }

class DesktopViews(object):

    def __init__(self, request):
        self.request = request

    @view_config(route_name='home', renderer='templates/home.pt')
    def home(self):

        return {
        }
