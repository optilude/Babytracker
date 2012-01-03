import os
import transaction

from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from babytracker.models import DBSession, Base, MyModel

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """

    if 'DATABASE_URL' in os.environ:
        settings['sqlalchemy.url'] = os.environ['DATABASE_URL']

    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)

    Base.metadata.create_all(engine)
    with transaction.manager:
        model = MyModel(name='one', value=1)
        DBSession.add(model)

    config = Configurator(settings=settings)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.scan()
    return config.make_wsgi_app()

