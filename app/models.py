# -*- coding: utf-8 -*-
"""
    app.models
    ~~~~~~~~~~

    Provides the SQLAlchemy models
"""
from __future__ import (
    absolute_import, division, print_function, with_statement,
    unicode_literals)

import savalidation.validators as val

from datetime import datetime as dt
from savalidation import ValidationMixin

from app import db


class Data(db.Model, ValidationMixin):
    # auto keys
    id = db.Column(db.Integer, primary_key=True)
    utc_created = db.Column(db.DateTime, nullable=False, default=dt.utcnow())
    utc_updated = db.Column(
        db.DateTime, nullable=False, default=dt.utcnow(), onupdate=dt.utcnow())

    # other keys
    mp_month = db.Column(db.String(4), nullable=False)
    cm_name = db.Column(db.String(64), nullable=False)
    adm0_name = db.Column(db.String(64), nullable=False)
    adm1_name = db.Column(db.String(128), nullable=False)
    mkt_name = db.Column(db.String(32), nullable=False)
    cm_name = db.Column(db.String(32), nullable=False)
    mp_price = db.Column(db.Numeric, nullable=False)
    mp_year = db.Column(db.Integer, nullable=False)

    # validation
    val.validates_constraints()

    def __repr__(self):
        return '<Age(%r)>' % self.dataset_name
