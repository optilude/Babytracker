from pyramid.view import view_config, view_defaults
from pyramid.security import remember, forget, authenticated_userid
from pyramid.httpexceptions import HTTPFound, HTTPForbidden

from babytracker.interfaces import IDesktopRequest
from babytracker.interfaces import SIGNUP_PERMISSION
from babytracker import models

# Until https://github.com/Pylons/pyramid/issues/394 is released
@view_defaults(for_=models.Root, request_type=IDesktopRequest)
class RootViews(object):

    def __init__(self, request):
        self.request = request

    @view_config(name='', renderer='babytracker:templates/home.pt')
    def home(self):

        return {
        }

    @view_config(name='signup', renderer='babytracker:templates/signup.pt', permission=SIGNUP_PERMISSION)
    def signup(self):
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
            elif password != confirm_password:
                errors['password'] = errors['confirm_password'] = u"Passwords do not match"

            if errors:
                self.request.session.flash(u"Invalid information entered. Please see below for details.", queue='error')

            session = models.DBSession()
            if not errors:
                existing_user = session.query(models.User).filter_by(email=email).first()
                if existing_user is not None:
                    # TODO: Offer password recovery
                    self.request.session.flash(u"A user with this email address already exists. Please use a different one", queue='error')
                    errors['email'] = u""

            if not errors:
                user = models.User(email, name, password)
                session.add(user)

                self.request.session.flash('Account created. You are now logged in.', queue='success')
                headers = remember(self.request, user.__name__)

                return HTTPFound(location=self.request.resource_url(user), headers=headers)

        return {
            'errors': errors,
        }

    @view_config(name='login', renderer='babytracker:templates/login.pt', permission=SIGNUP_PERMISSION)
    def login(self):
        errors = {}

        post = self.request.POST
        if 'btn.login' in post:
            email = post.get('email', None)
            password = post.get('password', None)

            if not email:
                errors['email'] = u"Email is required"
            elif not '@' in email: # crude, we know
                errors['email'] = u"Invalid email address"
            if not password:
                errors['password'] = u"Password is required"

            if errors:
                self.request.session.flash(u"Invalid information entered. Please see below for details.", queue='error')
            else:
                user = models.User.authenticate(email, password)
                if user is None:
                    self.request.session.flash(u"Incorrect email address or password. Please try again.", queue='error')
                else:
                    headers = remember(self.request, user.__name__)

                    self.request.session.flash('You are now logged in.', queue='success')

                    # TODO: Redirect to entry screen
                    return HTTPFound(location='/', headers=headers)

        return {
            'errors': errors
        }

    @view_config(name='logout', context=models.Root, request_type=IDesktopRequest)
    def logout(self):
        self.request.session.flash('You are now logged out.', queue='success')
        headers = forget(self.request)
        return HTTPFound(location='/', headers=headers)
