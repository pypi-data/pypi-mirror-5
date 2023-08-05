# -*- coding: utf-8 -*-
import logging
import pymongo
from copy import copy
import operator

from pyramid.config import Configurator

# logger has to be BEFORE the import of the following resources import
maxlogger = logging.getLogger('max')

from max.resources import Root, loadMAXSettings, loadMAXSecurity
from max.rest.resources import RESOURCES

from pyramid_beaker import set_cache_regions_from_settings
from max import debug

DEFAULT_CONTEXT_PERMISSIONS = dict(read='public', write='public', subscribe='public', invite='public')
CONVERSATION_PARTICIPANTS_LIMIT = 20
LAST_AUTHORS_LIMIT = 8
AUTHORS_SEARCH_MAX_QUERIES_LIMIT = 6


class RestrictedPredicate(object):
    def __init__(self, val, config):
        self.val = val

    def text(self):
        return 'Restricted permissions to = %s' % (self.val,)

    phash = text

    def __call__(self, context, request):
        # Extract the username and token from request headers
        username = request.headers.get('X-Oauth-Username', '')
        allowed_roles = copy(self.val)
        if not isinstance(self.val, list):
            allowed_roles = [self.val, ]
        security = request.registry.max_security
        user_has_roles = [username in security.get("roles").get(role) for role in allowed_roles]
        user_is_allowed = reduce(operator.and_, user_has_roles, True)

        return user_is_allowed


def main(global_config, **settings):
    """ This function returns a WSGI application.
    """

    # App config
    config = Configurator(settings=settings,
                          root_factory=Root)

    config.add_tween('max.tweens.post_tunneling_factory')

    debug.setup(config, settings)

    config.add_route('wadl', '/WADL')

    # Store in registry
    db_uri = settings['mongodb.url']
    conn = pymongo.Connection(db_uri)
    db = conn[settings['mongodb.db_name']]
    config.registry.max_store = db

    # Set MAX settings
    config.registry.max_settings = loadMAXSettings(settings, config)

    # Set security
    config.registry.max_security = loadMAXSecurity(config.registry)

    # Load cache settings
    set_cache_regions_from_settings(settings)

    # REST Resources
    # Configure routes based on resources defined in RESOURCES
    for name, properties in RESOURCES.items():
        config.add_route(name, properties.get('route'))

    config.scan('max', ignore=['max.tests', 'max.scripts'])

    config.add_view_predicate('restricted', RestrictedPredicate)

    return config.make_wsgi_app()
