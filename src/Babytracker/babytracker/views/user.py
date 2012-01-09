from pyramid.view import view_config, view_defaults

from babytracker.interfaces import IDesktopRequest
from babytracker.interfaces import VIEW_PERMISSION
from babytracker import models

import dateutil.parser

@view_defaults(for_=models.User, request_type=IDesktopRequest)
class UserViews(object):

    def __init__(self, request):
        self.request = request

    @view_config(name='', renderer='../templates/user.pt', permission=VIEW_PERMISSION)
    def index(self):

        errors = {}
        user = self.request.context

        post = self.request.POST
        if 'btn.save' in post:
            name = post.get('name', None)
            if not name:
                errors['name'] = u"Name is required"
                self.request.session.flash(u"Invalid name entered. Please try again.", queue='error')

            if not errors:
                user.name = name
                self.request.session.flash(u"Details updated", queue="success")

        if 'btn.change_password' in post:
            password = post.get('password', None)
            confirm_password = post.get('confirm_password', None)

            if not password:
                errors['password'] = u"Password is required"
            elif password != confirm_password:
                errors['password'] = errors['confirm_password'] = u"Passwords do not match"

            if errors:
                self.request.session.flash(u"Unable to change password. Please try again.", queue='error')
            else:
                user.change_password(password)
                self.request.session.flash(u"Password changed", queue="success")

        if 'btn.add_baby' in post:
            baby_name = post.get('baby_name', None)
            baby_gender = post.get('baby_gender', None)
            baby_dob = post.get('baby_dob', None)

            if not baby_name:
                errors['baby_name'] = u"Name is required"
            if baby_gender not in ('m', 'f'):
                errors['baby_gender'] = u"Invalid gender"

            try:
                baby_dob = dateutil.parser.parse(baby_dob)
            except ValueError:
                errors['baby_dob'] = u"Invalid date entered"

            if errors:
                self.request.session.flash(u"Unable to add baby. Please try again.", queue='error')
            else:
                user.babies.append(models.Baby(user, baby_dob, baby_name, baby_gender))
                self.request.session.flash(u"Baby added", queue="success")

        return {
            'errors': errors,
        }
