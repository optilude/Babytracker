import urllib
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

        headers = forget(self.request)
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
            'email': 'test@example.org',     // User's email address
            'name' : 'Jack Smith',           // User's full name
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
        403 -> Conception Denied
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
            dob_date = dateutil.parser.parse(dob).date()
        except ValueError:
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
            'name'  : 'Jill',                      // Baby name
            'dob'   : '2011-01-01',                // Baby date of birth
            'gender': 'f'                          // Baby gender
        }

        403 -> Not authorised to view this baby
        """

        return baby_json(self.request.context)

    @view_config(name='entries', request_method='GET', permission=VIEW_PERMISSION)
    def entries(self):
        """Entries recorded for the baby

        GET /api/test@example.org/jill/entries?start=2011-01-01T12:00:00&end=2011-01-01T12:00:00&entry_type=breast_feed

        start and end contain ISO formatted dates or date-times to bound the
        returned list. entry_type limits to one type of entry only. All
        parameters are optional.

        200 -> [
            {
                'url'   : '/api/test@example.org/jill/1', // Entry URL

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

        400 -> Invalid date format
        403 -> Not authorised to view information about this baby
        """

        start_date = None
        end_date = None

        start = self.request.GET.get('start', None)
        end = self.request.GET.get('end', None)
        entry_type = self.request.GET.get('entry_type', None)

        if start is not None:
            try:
                start_date = dateutil.parser.parse(start)
            except ValueError:
                raise HTTPBadRequest("Invalid start date")

        if end is not None:
            try:
                end_date = dateutil.parser.parse(end)
            except ValueError:
                raise HTTPBadRequest("Invalid end date")

        return [
            entry_json(entry, self.request)
            for entry in self.request.context.get_entries_between(
                start=start_date,
                end=end_date,
                entry_type=entry_type,
            )
        ]

    @view_config(name='', request_method='PUT', permission=EDIT_PERMISSION)
    def edit(self):
        """Update the baby

        PUT /api/test@example.org/jill
        {
            'name'  : 'Jillie',       // Optional
            'dob'   : '2011-01-01',   // Optional
            'gender': 'f'             // Optional, should be 'm' or 'f'
        }

        200 -> {
            'url'   : '/api/test@example.org/jillie' // Baby URL - may change!
            'name'  : 'Jillie',                      // Baby name
            'dob'   : '2011-01-01',                  // Baby date of birth
            'gender': 'f'                            // Baby gender
        }

        400 -> Invalid date of birth, gender or no keys supplied
        409 -> Name is used by another baby
        403 -> Not authorised to edit this baby
        }
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

        if not name and not dob and not gender:
            raise HTTPBadRequest("JSON object with 'name', 'dob' and/or 'gender' expected")

        if gender and gender not in ('m', 'f'):
            raise HTTPBadRequest("gender must be 'm' or 'f'")

        dob_date = None

        if dob:
            try:
                dob_date = dateutil.parser.parse(dob).date()
            except ValueError:
                raise HTTPBadRequest("Invalid dob date")

        baby = self.request.context
        normalized_name = models.Baby.normalize_name(name)
        baby_name = baby.__name__

        for b in self.request.context.babies:
            if b.__name__ != baby_name and b.__name__ == normalized_name:
                raise HTTPConflict(u"Baby with name %s already exists" % name)

        if dob_date:
            baby.dob = dob_date
        if name:
            baby.name = name
        if gender:
            baby.gender = gender

        return baby_json(baby, self.request)

    @view_config(name='', request_method='DELETE', permission=EDIT_PERMISSION)
    def delete(self):
        """Delete the baby

        DELETE /api/test@example.org/jill

        200 -> {
            'url' : '/api/test@example.org', // API root for user
            'email': 'test@example.org',     // User's email address
            'name' : 'John Smith',           // User's full name
            'babies': [
                ...
            ]
        }

        403 -> Not authorised to delete this baby
        """

        baby = self.request.context
        user = baby.user

        session = models.DBSession()
        session.delete(baby)
        session.flush()

        return user_json(user, self.request)

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

        400 -> Invalid request parameters
        403 -> Not authorised to create entry for this baby
        """

        try:
            body = self.request.json_body
        except ValueError, e:
            raise HTTPBadRequest(str(e))

        if not isinstance(body, dict):
            raise HTTPBadRequest("JSON object expected")

        entry_type = body.get('entry_type')
        start = body.get('start')
        end = body.get('end')
        note = body.get('note')

        start_date = end_date = None

        if not entry_type or not start:
            raise HTTPBadRequest("JSON object with 'entry_type' and 'start' expected")

        try:
            start_date = dateutil.parser.parse(start)
        except ValueError:
            raise HTTPBadRequest("Invalid start date")

        if end:
            try:
                end_date = dateutil.parser.parse(end)
            except ValueError:
                raise HTTPBadRequest("Invalid end date")

        factory = models.lookup_entry_type(entry_type)
        if factory is None:
            raise HTTPBadRequest(u"Unknown entry_type: %s" % entry_type)

        kwargs = {
            'baby': self.request.context,
            'start': start_date,
            'end': end_date,
            'note': note
        }

        for key, value in body.items():
            if key not in kwargs and key != 'entry_type':
                # Convert value to correct builtin type based on SQLAlchemy
                # column spec

                attr = getattr(factory, key, None)
                if attr is None:
                    raise HTTPBadRequest(u"Unknown property %s of type %s" % (key, entry_type,))

                try:
                    value = attr.property.columns[0].type.python_type(value)
                except (AttributeError, ValueError,), e:
                    raise HTTPBadRequest(u"Incompatible property %s of type %s: %s" % (key, entry_type, str(e)))

                kwargs[key] = value

        session = models.DBSession()
        entry = factory(**kwargs)
        session.add(entry)

        return entry_json(entry, self.request)

@view_defaults(context=models.Entry, route_name='api', renderer='json')
class EntryAPI(object):

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

            'left_duration': 10,            // For 'breast_feed' or 'mixed_feed'
            'right_duration': 0,            // For 'breast_feed' or 'mixed_feed'
            'amount': 100,                  // For 'bottle_feed'
            'topup': 120,                   // For 'mixed_feed'
            'duration': 30,                 // For 'sleep', in minutes
            'contents': 'wet',              // For 'dirty' or 'none', for 'nappy_change'
        }

        403 -> Not authorised to view details about this entry
        """

        return entry_json(self.request.context, self.request)

    @view_config(name='', request_method='PUT', permission=EDIT_PERMISSION)
    def edit(self):
        """Update the baby

        PUT /api/test@example.org/jill/1
        {
            'start': '2012-01-01 12:21:00', // Optional
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

            'entry_type': 'breast_feed',
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

        400 -> Invalid parameters
        403 -> Not authorised to edit this entry
        """

        try:
            body = self.request.json_body
        except ValueError, e:
            raise HTTPBadRequest(str(e))

        if not isinstance(body, dict):
            raise HTTPBadRequest("JSON object expected")

        entry = self.request.context

        if 'start' in body:
            try:
                start_date = dateutil.parser.parse(body['start'])
            except ValueError:
                raise HTTPBadRequest("Invalid start date")

            entry.start = start_date

        if 'end' in body:
            try:
                end_date = dateutil.parser.parse(body['end'])
            except ValueError:
                raise HTTPBadRequest("Invalid end date")

            entry.end = end_date

        if 'note' in body:
            note = body['note']
            if not isinstance(note, basestring):
                raise HTTPBadRequest("Invalid note")
            entry.note = note

        for key, value in body.items():
            if key not in ('id', 'type', 'start', 'end', 'note', 'baby', 'baby_id',):
                # Convert value to correct builtin type based on SQLAlchemy
                # column spec

                attr = getattr(entry.__class__, key, None)
                if attr is None:
                    raise HTTPBadRequest(u"Unknown property %s of type %s" % (key, entry.type,))

                try:
                    value = attr.property.columns[0].type.python_type(value)
                except (AttributeError, ValueError,), e:
                    raise HTTPBadRequest(u"Incompatible property %s of type %s: %s" % (key, entry.type, str(e)))

                setattr(entry, key, value)

        return entry_json(entry, self.request)

    @view_config(name='', request_method='DELETE', permission=EDIT_PERMISSION)
    def delete(self):
        """Delete the entry

        DELETE /api/test@example.org/jill/1

        200 -> {
            'url'   : '/api/test@example.org/jill' // Baby URL
            'name'  : 'Jill',                      // Baby name
            'dob'   : '2011-01-01',                // Baby date of birth
            'gender': 'f'                          // Baby gender
        }

        403 -> Not authorised to delete this entry
        """

        entry = self.request.context
        baby = entry.baby

        session = models.DBSession()
        session.delete(entry)
        session.flush()

        return baby_json(baby, self.request)
