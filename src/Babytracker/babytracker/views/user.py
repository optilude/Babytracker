from pyramid.view import view_config, view_defaults

from babytracker.interfaces import VIEW_PERMISSION
from babytracker import models

import dateutil.parser

@view_defaults(context=models.User)
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
                baby = models.Baby(user, baby_dob.date(), baby_name, baby_gender)
                session = models.DBSession()
                session.add(baby)
                self.request.session.flash(u"Baby added", queue="success")

        if 'btn.edit_baby' in post:
            baby_id = post.get('baby_id', None)
            baby_name = post.get('baby_name', None)
            baby_gender = post.get('baby_gender', None)
            baby_dob = post.get('baby_dob', None)

            if not baby_name:
                errors['edit_baby_name'] = u"Name is required"
            if baby_gender not in ('m', 'f'):
                errors['edit_baby_gender'] = u"Invalid gender"

            try:
                baby_dob = dateutil.parser.parse(baby_dob)
            except ValueError:
                errors['edit_baby_dob'] = u"Invalid date entered"

            if errors:
                self.request.session.flash(u"Unable to edit baby. Please try again.", queue='error')
            else:
                baby = None
                for b in user.babies:
                    if b.__name__ == baby_id:
                        baby = b
                        break

                if baby is None:
                    self.request.session.flash(u"Baby not found. It may have been deleted already.", queue='error')
                else:
                    session = models.DBSession()

                    baby.name = baby_name
                    baby.gender = baby_gender
                    baby.dob = baby_dob.date()

                    self.request.session.flash(u"Baby details updated", queue="success")

        if 'btn.delete_baby' in post:
            baby_id = post.get('baby_id')

            if not baby_id:
                self.request.session.flash(u"Missing baby name - this should not happen", queue='error')

            else:
                baby = None
                for b in user.babies:
                    if b.__name__ == baby_id:
                        baby = b
                        break

                if baby is None:
                    self.request.session.flash(u"Baby not found. It may have been deleted already.", queue='error')
                else:
                    session = models.DBSession()
                    session.delete(baby)
                    session.flush()

                    session.refresh(user);

                    self.request.session.flash(u"Baby deleted", queue="success")

        return {
            'errors': errors,
        }
