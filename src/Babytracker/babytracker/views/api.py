from pyramid.view import view_config, view_defaults
from pyramid.security import remember, forget

from babytracker.interfaces import VIEW_PERMISSION, EDIT_PERMISSION, SIGNUP_PERMISSION
from babytracker import models

@view_defaults(context=models.Root, route_name='api', renderer='json')
class RootAPI(object):

    def __init__(self, request):
        self.request = request

    @view_config(request_method='GET')
    def index(self):
        """Discover services

        GET /

        200 -> {
            'login_url' : '/api/login', // API URL for logging in
            'logout_url': /api/logout'  // API URL for logging out
        }
        """

        return {}
    
    @view_config(name='login', request_method='POST', permission=SIGNUP_PERMISSION)
    def login(self):
        """Log in and retreive basic information about the user

        POST /api/login
        {
            'username': 'test@example.org', // Username
            'password': 'secret'            // Password
        }

        200 -> {
            'url' : '/api/users/test@example.org', // API root for user
            'email': 'test@example.org',           // User's email address
            'name' : 'John Smith',                 // User's full name
            'babies': [
                {
                    'url'   : '/api/users/test@example.org/jill' // Baby URL
                    'name'  : 'Jill',                            // Baby name
                    'dob'   : '2011-01-01',                      // Baby date of birth
                    'gender': 'f'                                // Baby gender
                },
                ...
            ]
        }

        401 -> {
            'error_detail': {
                'message': 'Invalid credentials'
            }
        }
        """

        return {}
    
    @view_config(name='logout', request_method='POST')
    def logout(self):
        """Log out as the current user

        POST /api/logout

        200 -> {
            'url' : '/' // URL to home
        }

        403 -> {
            'error_detail': {
                'message': 'User not logged in'
            }
        }
        """

        return {}

@view_defaults(context=models.User, route_name='api', renderer='json')
class UserAPI(object):

    def __init__(self, request):
        self.request = request

    @view_config(name='', request_method='GET', permission=VIEW_PERMISSION)
    def index(self):
        """Details about the user

        GET /api/users/test@example.org

        200 -> {
            'url' : '/api/users/test@example.org', // API root for user
            'email': 'test@example.org',           // User's email address
            'name' : 'John Smith',                 // User's full name
            'babies': [
                {
                    'url'   : '/api/users/test@example.org/jill' // Baby URL
                    'name'  : 'Jill',                            // Baby name
                    'dob'   : '2011-01-01',                      // Baby date of birth
                    'gender': 'f'                                // Baby gender
                },
                ...
            ]
        }

        403 -> {
            'error_detail': {
                'message': 'Not authorised to view details about this user'
            }
        }
        """

        return {}

    @view_config(name='', request_method='PUT', permission=EDIT_PERMISSION)
    def edit(self):
        """Update the user

        PUT /api/users/test@example.org
        {
            'name': 'Jack Smith', // optional
            'password': 'sikrit', // optional
        }

        200 -> {
            'url' : '/api/users/test@example.org', // API root for user
            'email': 'test@example.org',           // User's email address
            'name' : 'Jack Smith',                 // User's full name
            'babies': [
                {
                    'url'   : '/api/users/test@example.org/jill' // Baby URL
                    'name'  : 'Jill',                            // Baby name
                    'dob'   : '2011-01-01',                      // Baby date of birth
                    'gender': 'f'                                // Baby gender
                },
                ...
            ]
        }

        403 -> {
            'error_detail': {
                'message': 'Not authorised to edit this user'
            }
        }
        """

        return {}

    @view_config(name='', request_method='POST', permission=EDIT_PERMISSION)
    def create(self):
        """Create a new baby

        POST /api/users/test@example.org
        {
            'name': 'James',
            'dob': '2012-01-01',
            'gender': 'm'
        }

        200 -> {
            'url'   : '/api/users/test@example.org/james' // Baby URL
            'name'  : 'James',                            // Baby name
            'dob'   : '2012-01-01',                       // Baby date of birth
            'gender': 'm'                                 // Baby gender
        }

        403 -> {
            'error_detail': {
                'message': 'Conception Denied'
            }
        }
        """

        return {}

@view_defaults(context=models.Baby, route_name='api', renderer='json')
class BabyAPI(object):

    def __init__(self, request):
        self.request = request

    @view_config(name='', request_method='GET', permission=VIEW_PERMISSION)
    def index(self):
        """Details about the baby

        GET /api/users/test@example.org/jill

        200 -> {
            'url'   : '/api/users/test@example.org/jill' // Baby URL
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

    @view_config(name='', request_method='PUT', permission=EDIT_PERMISSION)
    def edit(self):
        """Update the baby

        PUT /api/users/test@example.org/jill
        {
            'name'  : 'Jillie',       // Optional
            'dob'   : '2011-01-01',   // Optional
            'gender': 'f'             // Optional
        }

        200 -> {
            'url'   : '/api/users/test@example.org/jillie' // Baby URL - may change!
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

        DELETE /api/users/test@example.org/jill

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

        POST /api/users/test@example.org/jill
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
            'url'   : '/api/users/test@example.org/jill/1' // Entry URL

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

        DELETE /api/users/test@example.org/jill

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

        GET /api/users/test@example.org/jill/1

        200 -> {
            'url'   : '/api/users/test@example.org/jill/1' // Entry URL

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

        PUT /api/users/test@example.org/jill/1
        {
            'start': '2012-01-01 12:21:00',
            'end': '2012-01-01 12:30:00',   // Optional
            'note': 'Note text',            // Optional

            'left_duration': 10,
            'right_duration': 0,
        }

        200 -> {
            'url'   : '/api/users/test@example.org/jill/1' // Entry URL

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

        GET /api/users/test@example.org/jill/1

        200 -> {
            'url'   : '/api/users/test@example.org/jill/1' // Entry URL

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

        PUT /api/users/test@example.org/jill/1
        {
            'start': '2012-01-01 12:21:00',
            'end': '2012-01-01 12:30:00',   // Optional
            'note': 'Note text',            // Optional

            'amount': 100,
        }

        200 -> {
            'url'   : '/api/users/test@example.org/jill/1' // Entry URL

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

        GET /api/users/test@example.org/jill/1

        200 -> {
            'url'   : '/api/users/test@example.org/jill/1' // Entry URL

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

        PUT /api/users/test@example.org/jill/1
        {
            'start': '2012-01-01 12:21:00',
            'end': '2012-01-01 12:30:00',   // Optional
            'note': 'Note text',            // Optional

            'left_duration': 10,
            'right_duration': 0,
            'topup': 120,
        }

        200 -> {
            'url'   : '/api/users/test@example.org/jill/1' // Entry URL

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

        GET /api/users/test@example.org/jill/1

        200 -> {
            'url'   : '/api/users/test@example.org/jill/1' // Entry URL

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

        PUT /api/users/test@example.org/jill/1
        {
            'start': '2012-01-01 12:21:00',
            'end': '2012-01-01 12:30:00',   // Optional
            'note': 'Note text',            // Optional

            'duration': 100,
        }

        200 -> {
            'url'   : '/api/users/test@example.org/jill/1' // Entry URL

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

        GET /api/users/test@example.org/jill/1

        200 -> {
            'url'   : '/api/users/test@example.org/jill/1' // Entry URL

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

        PUT /api/users/test@example.org/jill/1
        {
            'start': '2012-01-01 12:21:00',
            'end': '2012-01-01 12:30:00',   // Optional
            'note': 'Note text',            // Optional

            'contents': 'wet',
        }

        200 -> {
            'url'   : '/api/users/test@example.org/jill/1' // Entry URL

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
