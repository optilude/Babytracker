import os

from pyramid.config import Configurator
from pyramid.session import UnencryptedCookieSessionFactoryConfig

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

from sqlalchemy import engine_from_config

from babytracker.models import DBSession, Base, Root
from babytracker.security import validate_user

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

    session_factory = UnencryptedCookieSessionFactoryConfig(
        secret=settings.get('session-secret', 'secret'),
    )

    authn_policy = AuthTktAuthenticationPolicy(
        secret=settings.get('authentication-secret', 'secret'),
        callback=validate_user,
    )
    authz_policy = ACLAuthorizationPolicy()

    config = Configurator(
        settings=settings,
        root_factory=Root,
        session_factory=session_factory,
        authentication_policy=authn_policy,
        authorization_policy=authz_policy
    )

    config.add_static_view('static', 'static', cache_max_age=3600)

    config.scan()
    return config.make_wsgi_app()

