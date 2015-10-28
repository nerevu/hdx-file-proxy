# -*- coding: utf-8 -*-
"""
    app.utils
    ~~~~~~~~~

    Provides misc utility functions
"""
from __future__ import (
    absolute_import, division, print_function, with_statement,
    unicode_literals)

import itertools as it
import requests

from json import dumps, loads, JSONEncoder
from ast import literal_eval
from tempfile import SpooledTemporaryFile
from os.path import splitext

from flask import make_response, request
from ckanapi import RemoteCKAN as CKAN
from tabutils import io, convert as cv


def fetch_data(config):
    """Fetches realtime data and generates records"""
    ckan = CKAN(config['ENDPOINT'], apikey=config['API_KEY'])
    # r = ckan.fetch_resource(config['RID'])  # if using ckanutils
    resource = ckan.action.resource_show(id=config['RID'])
    url = resource.get('perma_link') or resource.get('url')
    r = requests.get(url, stream=True)

    if any('403' in h.headers.get('x-ckan-error', '') for h in r.history):
        raise NotAuthorized(
            'Access to fetch resource %s was denied.' % config['RID'])

    try:
        ext = splitext(url)[1].split('.')[1]
    except IndexError:
        ext = cv.ctype2ext(r.headers['Content-Type'])

    if ext == 'csv':
        records = io.read_csv(r.raw, sanitize=True, encoding=r.encoding)
    elif ext in {'xls', 'xlsx'}:
        r = requests.get(url)
        f = SpooledTemporaryFile()
        f.write(r.content)
        records = io.read_xls(f, sanitize=True, encoding=r.encoding)
    else:
        msg = 'Filetype `%s` unsupported.'
        msg += 'Please view tabutils.io documentation for assistance.'
        raise TypeError(msg)

    constraints = [('adm0_name', 'a'), ('mp_month', '3'), ('mp_year', '2015')]

    filterer = lambda x: all(x[k].lower().startswith(v) for k, v in constraints)
    return it.ifilter(filterer, records)

