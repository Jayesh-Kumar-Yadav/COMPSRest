"""Main entry point
"""
from pyramid.config import Configurator
from pyramid.renderers import JSONP

from urlparse import urlparse
import pymongo


def main(global_config, **settings):
    config = Configurator(settings=settings)
    config.include('pyramid_mako')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_renderer('jsonp', JSONP(param_name='callback'))

    config.add_route('crow_provider', '/provider')
    config.add_route('crow_layers', '/layers')
    config.add_route('crow_environment_json',
                     '/datasets')
    config.add_route('layer_kml',
                     '/kml')

    db_url = urlparse(settings['mongo_uri'])
    config.registry.db = pymongo.Connection(
        host=db_url.hostname,
        port=db_url.port
    )

    def add_db(request):
        db = config.registry.db[db_url.path[1:]]
        if db_url.username and db_url.password:
            db.authenticate(db_url.username, db_url.password)
        return db

    config.add_request_method(add_db, 'db', reify=True)

    config.scan("compsrest.views")
    return config.make_wsgi_app()
