# -*- encoding: utf-8 -*-
"""
Creating the user Class to handle register login etc... Not my code. Should work

License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

from app         import db
from flask_login import UserMixin

class User(UserMixin, db.Model):

    id       = db.Column(db.Integer,     primary_key=True)
    user     = db.Column(db.String(64),  unique = True)
    email    = db.Column(db.String(120), unique = True)
    password = db.Column(db.String(500))

    def __init__(self, user, email, password):
        self.user       = user
        self.password   = password
        self.email      = email

    def __repr__(self):
        return str(self.id) + ' - ' + str(self.user)

    def save(self):

        # inject self into db session
        db.session.add ( self )

        # commit change and save the object
        db.session.commit( )

        return self


"""
The brand will be the main entity. It will be composed of multiple
hashtags (named keywords because some plateforms don't have hashtags).
An user can create multiple brands and a number of linked keywords.
"""
class Brand(db.Model):

    id        = db.Column(db.Integer,      primary_key=True)
    brandname = db.Column(db.String(120),  unique = True)

    def __init__(self, brandname):
        self.id          = brand
        self.brandname   = brandname

    def __repr__(self):
        return str(self.id) + ' - ' + str(self.brandname)

    def save(self):

        # inject self into db session
        db.session.add ( self )

        # commit change and save the object
        db.session.commit( )

        return self

class Keyword(db.Model):

    id      = db.Column(db.Integer,      primary_key=True)
    keyword = db.Column(db.String(120),  unique = True)
    active  = db.Column(db.Boolean)

    def __init__(self, keyword, active):
        self.keyword     = keyword
        self.active      = active

    def __repr__(self):
        return str(self.id) + ' - ' + str(self.keyword)

    def save(self):

        # inject self into db session
        db.session.add ( self )

        # commit change and save the object
        db.session.commit( )

        return self
