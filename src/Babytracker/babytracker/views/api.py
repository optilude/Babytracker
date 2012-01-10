import urllib
import datetime
import dateutil.parser

from pyramid.view import view_config, view_defaults
from pyramid.traversal import resource_path
from pyramid.httpexceptions import HTTPBadRequest, HTTPUnauthorized, HTTPConflict
from pyramid.security import remember, forget

from babytracker.interfaces import VIEW_PERMISSION, EDIT_PERMISSION, SIGNUP_PERMISSION
from babytracker import models

def api_resource_path(context, request):
    return request.current_route_path(traverse=urllib.unquote(resource_path(context)[1:]))

def user_json(user, request):
    data = user.to_json_dict()
    data['url'] = api_resource_path(user, request)
    data['babies'] = [baby_json(baby, request) for baby in user.babies]
    return data

def baby_json(baby, request):
    data = baby.to_json_dict()
    data['url'] = api_resource_path(baby, request)
    return data

def entry_json(entry, request):
    data = entry.to_json_dict()
    data['url'] = api_resource_path(entry, request)
    return data

@view_defaults(context=models.Root, route_name='api', renderer='json')
class RootAPI(object):

    def __init__(self, request):
        self.request = request

    @view_config(request_method='GET')
    def index(self):
        """Discover services

        GET /

        200 -> {
            'login_url' : '/api/@@login', // API URL for logging in
            'logout_url': /api/@@logout'  // API URL for logging out
        }
        """

        prefix = api_resource_path(self.request.context, self.request)

        return {
            'login_url': prefix + '@@login',
            'logout_url': prefix + '@@logout',
        }

    @view_config(name='login', request_method='POST', permission=SIGNUP_PERMISSION)
    def login(self):
        """Log in and retreive basic information about the user

        POST /api/login
        {
            'username': 'test@example.org', // Username
            'password': 'secret'            // Password
        }

        200 -> {
            'url' : '/api/test@example.org', // API root for user
            'email': 'test@example.org',     // User's email address
            'name' : 'John Smith',           // User's full name
            'babies': [
                {
                    'url'   : '/api/test@example.org/jill' // Baby URL
                    'name'  : 'Jill',                      // Baby name
                    'dob'   : '2011-01-01',                // Baby date of birth
                    'gender': 'f'                          // Baby gender
                },
                ...
            ]
        }

        400 -> No username and/or no password
        401 -> Invalid credentials
        403 -> Already logged in
        """

        try:
            body = self.request.json_body
        except ValueError, e:
            raise HTTPBadRequest(str(e))

        if not isinstance(body, dict):
            raise HTTPBadRequest("JSON object with 'username' and 'password' expected")

        username = body.get('username')
        password = body.get('password')

        if not password or not username:
            raise HTTPBadRequest("JSON object with 'username' and 'password' expected")

        user = models.User.authenticate(username, password)
        if user is None:
            raise HTTPUnauthorized("Invalid credentials")

        headers = remember(self.request, user.__name__)
        self.request.response.headers.update(headers)

        return user_json(user, self.request)

    @view_config(name='logout', request_method='POST')
    def logout(self):
        """Log out as the current user

        POST /api/logout

        200 -> {
            'url' : '/api' // URL to home
        }
        """

        headers = forget(self.request.context)
        self.request.response.headers.update(headers)

        return {
            'url': api_resource_path(self.request.context, self.request)
        }

@view_defaults(context=models.User, route_name='api', renderer='json')
class UserAPI(object):

    def __init__(self, request):
        self.request = request

    @view_config(name='', request_method='GET', permission=VIEW_PERMISSION)
    def index(self):
        """Details about the user

        GET /api/test@example.org

        200 -> {
            'url' : '/api/test@example.org', // API root for user
            'email': 'test@example.org',           // User's email address
            'name' : 'John Smith',                 // User's full name
            'babies': [
                {
                    'url'   : '/api/test@example.org/jill' // Baby URL
                    'name'  : 'Jill',                            // Baby name
                    'dob'   : '2011-01-01',                      // Baby date of birth
                    'gender': 'f'                                // Baby gender
                },
                ...
            ]
        }

        400 -> Neither name, nor password supplied
        403 -> Not logged in or attempting to access another user's details
        """

        return user_json(self.request.context, self.request)

    @view_config(name='', request_method='PUT', permission=EDIT_PERMISSION)
    def edit(self):
        """Update the user

        PUT /api/test@example.org
        {
            'name': 'Jack Smith', // optional
            'password': 'sikrit', // optional
        }

        200 -> {
            'url' : '/api/test@example.org', // API root for user
            'email': 'test@example.org',           // User's email address
            'name' : 'Jack Smith',                 // User's full name
            'babies': [
                {
                    'url'   : '/api/test@example.org/jill' // Baby URL
                    'name'  : 'Jill',                            // Baby name
                    'dob'   : '2011-01-01',                      // Baby date of birth
                    'gender': 'f'                                // Baby gender
                },
                ...
            ]
        }

        403 -> Not logged in or attempting to edit another user's details
        """

        try:
            body = self.request.json_body
        except ValueError, e:
            raise HTTPBadRequest(str(e))

        if not isinstance(body, dict):
            raise HTTPBadRequest("JSON object with 'name' and/or 'password' expected")

        name = body.get('name')
        password = body.get('password')

        if not password and not name:
            raise HTTPBadRequest("JSON object with 'name' and/or 'password' expected")

        if name:
            self.request.context.name = name
        if password:
            self.request.context.change_password(password)

        return user_json(self.request.context, self.request)

    @view_config(name='', request_method='POST', permission=EDIT_PERMISSION)
    def create(self):
        """Create a new baby

        POST /api/test@example.org
        {
            'name': 'James',
            'dob': '2012-01-01',
            'gender': 'm'
        }

        201 -> {
            'url'   : '/api/test@example.org/james' // Baby URL
            'name'  : 'James',                      // Baby name
            'dob'   : '2012-01-01',                 // Baby date of birth
            'gender': 'm'                           // Baby gender
        }

        400 -> name, dob or gender missing, or gender not 'm' or 'f'
        409 -> name already exists
        """

        try:
            body = self.request.json_body
        except ValueError, e:
            raise HTTPBadRequest(str(e))

        if not isinstance(body, dict):
            raise HTTPBadRequest("JSON object with 'name', 'dob' and 'gender' expected")

        name = body.get('name')
        dob = body.get('dob')
        gender = body.get('gender')

        if not name or not dob or not gender:
            raise HTTPBadRequest("JSON object with 'name', 'dob' and 'gender' expected")

        if gender not in ('m', 'f'):
            raise HTTPBadRequest("gender must be 'm' or 'f'")

        try:
            dob_date = dateutil.parser.parse(dob)
        except ValueError:
            raise HTTPBadRequest("Invalid dob date")

        if not isinstance(dob_date, datetime.date):
            raise HTTPBadRequest("Invalid dob date")

        normalized_name = models.Baby.normalize_name(name)
        for baby in self.request.context.babies:
            if baby.__name__ == normalized_name:
                raise HTTPConflict(u"Baby with name %s already exists" % name)

        session = models.DBSession()
        baby = models.Baby(self.request.context, dob_date, name, gender)
        session.add(baby)

        self.request.response.status_int = 201

        return baby_json(baby, self.request)

@view_defaults(context=models.Baby, route_name='api', renderer='json')
class BabyAPI(object):

    def __init__(self, request):
        self.request = request

    @view_config(name='', request_method='GET', permission=VIEW_PERMISSION)
    def index(self):
        """Details about the baby

        GET /api/test@example.org/jill

        200 -> {
            'url'   : '/api/test@example.org/jill' // Baby URL
            'name'  : 'Jill',                            // Baby name
            'dob'   : '2011-01-01',                      // Baby date of birth
            'gender': 'f'                                // Baby gender
        }

        403 -> {
            'error_detail': {
                'message': 'Not authorised to view details about this baby'
            }
        }
        """

        return {}

    @view_config(name='entries', request_method='GET', permission=VIEW_PERMISSION)
    def entries(self):
        """Entries recorded for the baby

        GET /api/test@example.org/jill/entries?start=2011-01-01T12:00:00&end=2011-01-01T12:00:00

        start and end contain ISO formatted dates or date-times to bound the
        returned list. Both are optional.

        200 -> [
            {
                'entry_type': 'sleep',          // Or 'breast_feed', 'bottle_feed', 'mixed_feed', 'sleep', 'nappy_change'
                'start': '2012-01-01 12:21:00',
                'end': '2012-01-01 12:30:00',   // Optional
                'note': 'Note text',            // Optional

                'left_duration': 10,            // For 'breast_feed' or 'mixed_feed'
                'right_duration': 0,            // For 'breast_feed' or 'mixed_feed'
                'amount': 100,                  // For 'bottle_feed'
                'topup': 120,                   // For 'mixed_feed'
                'duration': 30,                 // For 'sleep', in minutes
                'contents': 'wet',              // For 'dirty' or 'none', for 'nappy_change'
            },
            ...
        ]

        403 -> {
            'error_detail': {
                'message': 'Not authorised to view details about this baby'
            }
        }
        """

        return {}

    @view_config(name='', request_method='PUT', permission=EDIT_PERMISSION)
    def edit(self):
        """Update the baby

        PUT /api/test@example.org/jill
        {
            'name'  : 'Jillie',       // Optional
            'dob'   : '2011-01-01',   // Optional
            'gender': 'f'             // Optional
        }

        200 -> {
            'url'   : '/api/test@example.org/jillie' // Baby URL - may change!
            'name'  : 'Jillie',                            // Baby name
            'dob'   : '2011-01-01',                        // Baby date of birth
            'gender': 'f'                                  // Baby gender
        }

        403 -> {
            'error_detail': {
                'message': 'Not authorised to edit this baby'
            }
        }
        """

        return {}

    @view_config(name='', request_method='DELETE', permission=EDIT_PERMISSION)
    def delete(self):
        """Delete the baby

        DELETE /api/test@example.org/jill

        200 -> {
        }

        403 -> {
            'error_detail': {
                'message': 'Not authorised to delete this baby'
            }
        }
        """

        return {}

    @view_config(name='', request_method='POST', permission=EDIT_PERMISSION)
    def create(self):
        """Create a new entry

        POST /api/test@example.org/jill
        {
            'entry_type': 'sleep',          // Or 'breast_feed', 'bottle_feed', 'mixed_feed', 'sleep', 'nappy_change'
            'start': '2012-01-01 12:21:00',
            'end': '2012-01-01 12:30:00',   // Optional
            'note': 'Note text',            // Optional

            'left_duration': 10,            // For 'breast_feed' or 'mixed_feed'
            'right_duration': 0,            // For 'breast_feed' or 'mixed_feed'
            'amount': 100,                  // For 'bottle_feed'
            'topup': 120,                   // For 'mixed_feed'
            'duration': 30,                 // For 'sleep', in minutes
            'contents': 'wet',              // For 'dirty' or 'none', for 'nappy_change'
        }

        200 -> {
            'url'   : '/api/test@example.org/jill/1' // Entry URL

            'entry_type': 'sleep',          // Or 'breast_feed', 'bottle_feed', 'mixed_feed', 'sleep', 'nappy_change'
            'start': '2012-01-01 12:21:00',
            'end': '2012-01-01 12:30:00',   // Optional
            'note': 'Note text',            // Optional

            'left_duration': 10,            // For 'breast_feed' or 'mixed_feed'
            'right_duration': 0,            // For 'breast_feed' or 'mixed_feed'
            'amount': 100,                  // For 'bottle_feed'
            'topup': 120,                   // For 'mixed_feed'
            'duration': 30,                 // For 'sleep', in minutes
            'contents': 'wet',              // For 'dirty' or 'none', for 'nappy_change'
        }

        403 -> {
            'error_detail': {
                'message': 'Not authorised to create entry for this baby'
            }
        }
        """

        return {}

@view_defaults(context=models.Entry, route_name='api', renderer='json')
class EntryAPI(object):

    @view_config(name='', request_method='DELETE', permission=EDIT_PERMISSION)
    def delete(self):
        """Delete the entry

        DELETE /api/test@example.org/jill

        200 -> {
        }

        403 -> {
            'error_detail': {
                'message': 'Not authorised to delete this entry'
            }
        }
        """

        return {}


@view_defaults(context=models.BreastFeed, route_name='api', renderer='json')
class BreastFeedAPI(object):

    def __init__(self, request):
        self.request = request

    @view_config(name='', request_method='GET', permission=VIEW_PERMISSION)
    def index(self):
        """Details about the entry

        GET /api/test@example.org/jill/1

        200 -> {
            'url'   : '/api/test@example.org/jill/1' // Entry URL

            'entry_type': 'breast_feed',
            'start': '2012-01-01 12:21:00',
            'end': '2012-01-01 12:30:00',   // Optional
            'note': 'Note text',            // Optional

            'left_duration': 10,
            'right_duration': 0,
        }

        403 -> {
            'error_detail': {
                'message': 'Not authorised to view details about this entry'
            }
        }
        """

        return {}

    @view_config(name='', request_method='PUT', permission=EDIT_PERMISSION)
    def edit(self):
        """Update the baby

        PUT /api/test@example.org/jill/1
        {
            'start': '2012-01-01 12:21:00',
            'end': '2012-01-01 12:30:00',   // Optional
            'note': 'Note text',            // Optional

            'left_duration': 10,
            'right_duration': 0,
        }

        200 -> {
            'url'   : '/api/test@example.org/jill/1' // Entry URL

            'entry_type': 'breast_feed',
            'start': '2012-01-01 12:21:00',
            'end': '2012-01-01 12:30:00',   // Optional
            'note': 'Note text',            // Optional

            'left_duration': 10,
            'right_duration': 0,
        }

        403 -> {
            'error_detail': {
                'message': 'Not authorised to edit this entry'
            }
        }
        """

        return {}

@view_defaults(context=models.BottleFeed, route_name='api', renderer='json')
class BottleFeedAPI(object):

    def __init__(self, request):
        self.request = request

    @view_config(name='', request_method='GET', permission=VIEW_PERMISSION)
    def index(self):
        """Details about the entry

        GET /api/test@example.org/jill/1

        200 -> {
            'url'   : '/api/test@example.org/jill/1' // Entry URL

            'entry_type': 'bottle_feed',
            'start': '2012-01-01 12:21:00',
            'end': '2012-01-01 12:30:00',   // Optional
            'note': 'Note text',            // Optional

            'amount': 100,
        }

        403 -> {
            'error_detail': {
                'message': 'Not authorised to view details about this entry'
            }
        }
        """

        return {}

    @view_config(name='', request_method='PUT', permission=EDIT_PERMISSION)
    def edit(self):
        """Update the baby

        PUT /api/test@example.org/jill/1
        {
            'start': '2012-01-01 12:21:00',
            'end': '2012-01-01 12:30:00',   // Optional
            'note': 'Note text',            // Optional

            'amount': 100,
        }

        200 -> {
            'url'   : '/api/test@example.org/jill/1' // Entry URL

            'entry_type': 'bottle_feed',
            'start': '2012-01-01 12:21:00',
            'end': '2012-01-01 12:30:00',   // Optional
            'note': 'Note text',            // Optional

            'amount': 100,
        }

        403 -> {
            'error_detail': {
                'message': 'Not authorised to edit this entry'
            }
        }
        """

        return {}

@view_defaults(context=models.MixedFeed, route_name='api', renderer='json')
class MixedFeedAPI(object):

    def __init__(self, request):
        self.request = request

    @view_config(name='', request_method='GET', permission=VIEW_PERMISSION)
    def index(self):
        """Details about the entry

        GET /api/test@example.org/jill/1

        200 -> {
            'url'   : '/api/test@example.org/jill/1' // Entry URL

            'entry_type': 'breast_feed',
            'start': '2012-01-01 12:21:00',
            'end': '2012-01-01 12:30:00',   // Optional
            'note': 'Note text',            // Optional

            'left_duration': 10,
            'right_duration': 0,
            'topup': 120,
        }

        403 -> {
            'error_detail': {
                'message': 'Not authorised to view details about this entry'
            }
        }
        """

        return {}

    @view_config(name='', request_method='PUT', permission=EDIT_PERMISSION)
    def edit(self):
        """Update the baby

        PUT /api/test@example.org/jill/1
        {
            'start': '2012-01-01 12:21:00',
            'end': '2012-01-01 12:30:00',   // Optional
            'note': 'Note text',            // Optional

            'left_duration': 10,
            'right_duration': 0,
            'topup': 120,
        }

        200 -> {
            'url'   : '/api/test@example.org/jill/1' // Entry URL

            'entry_type': 'breast_feed',
            'start': '2012-01-01 12:21:00',
            'end': '2012-01-01 12:30:00',   // Optional
            'note': 'Note text',            // Optional

            'left_duration': 10,
            'right_duration': 0,
            'topup': 120,
        }

        403 -> {
            'error_detail': {
                'message': 'Not authorised to edit this entry'
            }
        }
        """

        return {}

@view_defaults(context=models.Sleep, route_name='api', renderer='json')
class SleepAPI(object):

    def __init__(self, request):
        self.request = request

    @view_config(name='', request_method='GET', permission=VIEW_PERMISSION)
    def index(self):
        """Details about the entry

        GET /api/test@example.org/jill/1

        200 -> {
            'url'   : '/api/test@example.org/jill/1' // Entry URL

            'entry_type': 'breast_feed',
            'start': '2012-01-01 12:21:00',
            'end': '2012-01-01 12:30:00',   // Optional
            'note': 'Note text',            // Optional

            'duration': 100,
        }

        403 -> {
            'error_detail': {
                'message': 'Not authorised to view details about this entry'
            }
        }
        """

        return {}

    @view_config(name='', request_method='PUT', permission=EDIT_PERMISSION)
    def edit(self):
        """Update the baby

        PUT /api/test@example.org/jill/1
        {
            'start': '2012-01-01 12:21:00',
            'end': '2012-01-01 12:30:00',   // Optional
            'note': 'Note text',            // Optional

            'duration': 100,
        }

        200 -> {
            'url'   : '/api/test@example.org/jill/1' // Entry URL

            'entry_type': 'breast_feed',
            'start': '2012-01-01 12:21:00',
            'end': '2012-01-01 12:30:00',   // Optional
            'note': 'Note text',            // Optional

            'duration': 100,
        }

        403 -> {
            'error_detail': {
                'message': 'Not authorised to edit this entry'
            }
        }
        """

        return {}

@view_defaults(context=models.NappyChange, route_name='api', renderer='json')
class NappyChangeAPI(object):

    def __init__(self, request):
        self.request = request

    @view_config(name='', request_method='GET', permission=VIEW_PERMISSION)
    def index(self):
        """Details about the entry

        GET /api/test@example.org/jill/1

        200 -> {
            'url'   : '/api/test@example.org/jill/1' // Entry URL

            'entry_type': 'breast_feed',
            'start': '2012-01-01 12:21:00',
            'end': '2012-01-01 12:30:00',   // Optional
            'note': 'Note text',            // Optional

            'contents': 'wet',
        }

        403 -> {
            'error_detail': {
                'message': 'Not authorised to view details about this entry'
            }
        }
        """

        return {}

    @view_config(name='', request_method='PUT', permission=EDIT_PERMISSION)
    def edit(self):
        """Update the baby

        PUT /api/test@example.org/jill/1
        {
            'start': '2012-01-01 12:21:00',
            'end': '2012-01-01 12:30:00',   // Optional
            'note': 'Note text',            // Optional

            'contents': 'wet',
        }

        200 -> {
            'url'   : '/api/test@example.org/jill/1' // Entry URL

            'entry_type': 'breast_feed',
            'start': '2012-01-01 12:21:00',
            'end': '2012-01-01 12:30:00',   // Optional
            'note': 'Note text',            // Optional

            'contents': 'wet',
        }

        403 -> {
            'error_detail': {
                'message': 'Not authorised to edit this entry'
            }
        }
        """

        return {}
