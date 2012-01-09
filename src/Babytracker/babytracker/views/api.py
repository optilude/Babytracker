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

        return {
            'login_url': '',
            'logout_url': '',
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
        {
        }

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

    # @view_config(name='', request_method='POST', permission=EDIT_PERMISSION)
    # def create(self):
    #     """Create a new entry

    #     POST /api/users/test@example.org/jill
    #     {
            
    #     }

    #     200 -> {
    #         'url'   : '/api/users/test@example.org/jill/1' // Entry URL
            
    #     }

    #     403 -> {
    #         'error_detail': {
    #             'message': ''
    #         }
    #     }
    #     """

    #     return {}

# TODO: Entry API
