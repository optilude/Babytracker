from pyramid.view import view_config, view_defaults
from pyramid.security import remember, forget
from pyramid.httpexceptions import HTTPFound

from babytracker.interfaces import IMobileRequest

from babytracker import models

# Until https://github.com/Pylons/pyramid/issues/394 is released
# @view_defaults(for_=models.Root, request_type=IMobileRequest)
# @view_defaults(context=models.Root)
# class RootViews(object):

#     def __init__(self, request):
#         self.request = request

#     @view_config(name='', request_type=IMobileRequest, renderer='templates/mobile_home.pt')
#     def home(self):

#         return {
#         }
