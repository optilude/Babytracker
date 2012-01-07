import os

from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from babytracker.models import DBSession, Base

def setup_database(settings):
    if 'DATABASE_URL' in os.environ: # Used on Heroku
        settings['sqlalchemy.url'] = os.environ['DATABASE_URL']

    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)

    Base.metadata.create_all(engine)

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """

    setup_database(settings)

    config = Configurator(settings=settings)

    config.add_static_view('static', 'static', cache_max_age=3600)

    config.scan()
    return config.make_wsgi_app()

