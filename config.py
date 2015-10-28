# -*- coding: utf-8 -*-
"""
    config
    ~~~~~~

    Provides the flask configuration
"""
from __future__ import (
    absolute_import, division, print_function, with_statement,
    unicode_literals)

from os import path as p, getenv

# module vars
_basedir = p.dirname(__file__)

# configurable vars
__USER__ = 'reubano'
__APP_NAME__ = 'HDX-Age-API'
__YOUR_NAME__ = 'Reuben Cummings'
__YOUR_EMAIL__ = 'reubano@gmail.com'
__YOUR_WEBSITE__ = 'http://%s.github.io' % __USER__


class Config(object):
    ADMINS = frozenset([__YOUR_EMAIL__])
    HOST = '127.0.0.1'
    ENDPOINT = 'https://data.hdx.rwlabs.org'
    RID = 'b5b850a5-76da-4c33-a410-fd447deac042'
    API_KEY = getenv('CKAN_API_KEY', 'MY_API_KEY')
    PORT = int(getenv('PORT', 3000))

    # TODO: programatically get app name
    heroku_server = '%s.herokuapp.com' % __APP_NAME__

    if getenv('DATABASE_URL', False):
        SERVER_NAME = heroku_server

    REPO = 'https://github.com/%s/%s' % (__USER__, __APP_NAME__)
    API_METHODS = ['GET']
    API_MAX_RESULTS_PER_PAGE = 1000
    API_URL_PREFIX = '/v1'

    DEBUG = False
    TESTING = False
    PROD = False
    CHUNK_SIZE = 10000
    ROW_LIMIT = 0


class Production(Config):
    defaultdb = 'postgres://%s@localhost/app' % __USER__
    SQLALCHEMY_DATABASE_URI = getenv('DATABASE_URL', defaultdb)
    HOST = '0.0.0.0'
    PROD = True


class Development(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///%s' % p.join(_basedir, 'app.db')
    DEBUG = True
    CHUNK_SIZE = 10
    ROW_LIMIT = 50


class Test(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    ROW_LIMIT = 10
    TESTING = True
