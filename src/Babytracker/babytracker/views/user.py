from pyramid.view import view_config, view_defaults
from pyramid.traversal import resource_path
from pyramid.httpexceptions import HTTPFound

from babytracker.interfaces import VIEW_PERMISSION
from babytracker import models

import datetime
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

    @view_config(name='new-entry', renderer='../templates/new_entry.pt', permission=VIEW_PERMISSION)
    def new_entry(self):

        errors = {}
        response = {
            'errors': errors,
            'now': datetime.datetime.now()
        }
        post = self.request.POST

        if 'btn.save' in post:

            entry_type = post.get('entry_type')
            start_date_str = post.get('start', '')
            start_time_str = post.get('start_time', '')
            start = "%s %s" % (start_date_str, start_time_str,)
            start_date = None

            if not start:
                errors['start'] = u"Start date and time is required"

            if errors:
                self.request.session.flash(u"Unable to add entry. Please try again", queue='error')
                return response

            try:
                start_date = dateutil.parser.parse(start)
            except ValueError:
                errors['start'] = u"Invalid start date or time"

            if errors:
                self.request.session.flash(u"Unable to add entry. Please try again", queue='error')
                return response

            factory = models.lookup_entry_type(entry_type)
            if factory is None:
                self.request.session.flash(u"Invalid entry type - this should not happen", queue='error')
                return response

            entries = []

            for baby in self.request.context.babies:
                baby_name = baby.__name__

                end_date = end = None
                end_date_str = post.get('%s.end' % baby_name, '')
                end_time_str = post.get('%s.end_time' % baby_name, '')
                note = post.get('note', '')

                if end_time_str:
                    end = "%s %s" % (end_date_str, end_time_str,)
                    try:
                        end_date = dateutil.parser.parse(end)
                    except ValueError:
                        errors['end'] = u"Invalid end date or time"

                kwargs = {
                    'baby': baby,
                    'start': start_date,
                    'end': end_date,
                    'note': note
                }

                for key, value in post.items():
                    if (
                        key.startswith("%s." % baby_name) and
                        key not in kwargs and
                        key not in ('%s.end_time' % baby_name) and
                        value
                    ):
                        # Convert value to correct builtin type based on SQLAlchemy
                        # column spec

                        attr_name = key[len(baby_name)+1:]

                        attr = getattr(factory, attr_name, None)
                        if attr is None:
                            continue

                        type_ = attr.property.columns[0].type.python_type

                        try:
                            if type_ is datetime.timedelta:
                                value = datetime.timedelta(minutes=int(value))
                            else:
                                value = type_(value)
                        except (TypeError,AttributeError, ValueError,):
                            errors[key] = u"Invalid value"

                        kwargs[attr_name] = value

                entry = factory(**kwargs)
                entries.append(entry)

            if not errors:
                session = models.DBSession()
                for entry in entries:
                    session.add(entry)

                self.request.session.flash(u"Entry added", queue="success")

                return HTTPFound(location=resource_path(self.request.context) + '@@entries')

        return {
            'errors': errors,
            'now': datetime.datetime.now(),
        }

    @view_config(name='entries', renderer='../templates/entries.pt', permission=VIEW_PERMISSION)
    def entries(self):

        today = datetime.date.today();
        days = [today - datetime.timedelta(days=i) for i in range(7)]

        errors = {}
        response = {
            'errors': errors,
            'days': days,
        }

        return response