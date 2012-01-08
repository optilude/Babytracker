from pyramid.view import view_config, view_defaults
from babytracker.interfaces import IMobileRequest
from babytracker.interfaces import IDesktopRequest

from babytracker import models

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

    @view_config(name='signup', request_type=IDesktopRequest, renderer='templates/signup.pt')
    def signup(self):

        headline_error = None
        errors = {}

        post = self.request.POST
        if 'btn.signup' in post:
            email = post.get('email', None)
            name = post.get('name', None)
            password = post.get('password', None)
            confirm_password = post.get('confirm_password', None)

            if not email:
                errors['email'] = u"Email is required"
            elif not '@' in email: # crude, we know
                errors['email'] = u"Invalid email address"
            if not name:
                errors['name'] = u"Name is required"
            if not password:
                errors['password'] = u"Password is required"
                errors['confirm_password'] = u"Password confirmation is required"
            elif password != confirm_password:
                errors['password'] = errors['confirm_password'] = u"Passwords do not match"

            if errors:
                headline_error = u"Invalid information entered. Please see below for details."

            session = models.DBSession()
            if not errors:
                existing_user = session.query(models.User).filter_by(email=email).first()
                if existing_user is not None:
                    # TODO: Offer password recovery
                    headline_error = u"A user with this email address already exists. Please use a different one"
                    errors['email'] = u""

            if not errors:
                user = models.User(email, name, password)
                session.add(user)

                # TODO: Log in and redirect

                self.request.session.flash('Account created. You are now logged in.', queue='success')

        return {
            'errors': errors,
            'headline_error': headline_error,
        }