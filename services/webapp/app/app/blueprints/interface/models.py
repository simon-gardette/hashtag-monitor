# -*- encoding: utf-8 -*-

from flask_login import UserMixin
from sqlalchemy import Binary, Column, Integer, String
from sqlalchemy.dialects.postgresql import JSONB

from app.extensions import db, login_manager

from datetime import datetime


class Brands(db.Model):

    __tablename__ = "brands"

    id = db.Column(db.Integer, primary_key=True)
    brand_name = db.Column(db.String(255), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.now)


    def __repr__(self):
        return str(self.id)


class Keywords(db.Model):

    __tablename__ = "keywords"


    id = db.Column(db.Integer, primary_key=True)
    brand_id = db.Column(db.Integer, db.ForeignKey('brands.id'), nullable=False)
    brand = db.relationship('Brands')
    keyword_name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)


    def __repr__(self):
        return str(self.id)

class ExcludedKeywords(db.Model):

    __tablename__ = "excluded_keywords"


    id = db.Column(db.Integer, primary_key=True)
    brand_id = db.Column(db.Integer, db.ForeignKey('brands.id'), nullable=False)
    brand = db.relationship('Brands')
    keyword_name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return str(self.id)

class Platforms(db.Model):

    __tablename__ = "platforms"

    id = db.Column(db.Integer, primary_key=True)
    platform_name = db.Column(db.String(150), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return str(self.id)


class Raws(db.Model):

    __tablename__ = "raws"

    id = db.Column(db.Integer, primary_key=True)
    brand_id = db.Column(db.Integer, db.ForeignKey('brands.id'), nullable=False)
    brand = db.relationship('Brands')
    keyword_id = db.Column(db.Integer, db.ForeignKey('keywords.id'), nullable=False)
    keyword = db.relationship('Keywords')
    platform_id = db.Column(db.Integer, db.ForeignKey('platforms.id'), nullable=False)
    platform = db.relationship('Platforms')
    api_id = db.Column(db.String(255), nullable=False, unique=True)
    raw_data =  db.Column(JSONB, nullable=False)
    status =  db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return str(self.id)

class Tweets(db.Model):

    __tablename__ = "tweets"

    id = db.Column(db.Integer, primary_key=True)
    keyword_id = db.Column(db.Integer, db.ForeignKey('keywords.id'), nullable=False)
    keyword = db.relationship('Keywords')
    raw_id = db.Column(db.Integer, db.ForeignKey('raws.id'), nullable=False)
    raw = db.relationship('Raws')
    brand_id = db.Column(db.Integer, db.ForeignKey('brands.id'), nullable=False)
    brand = db.relationship('Brands')
    twitter_id = db.Column(db.String(255))
    twitter_user_id = db.Column(db.String(255))
    twitter_user_name = db.Column(db.String(255))
    twitter_followers_count = db.Column(db.Integer)
    twitter_media_url = db.Column(db.String(255))
    twitter_sentiment = db.Column(db.String(255)) # 0 negative, 1 neutral, 2 positive
    twitter_text  = db.Column(db.Text)
    twitter_lang  = db.Column(db.String(255))
    twitter_url  = db.Column(db.String(255))
    twitter_topics  = db.Column(db.String(255))
    tokenizer = db.Column(db.ARRAY)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return str(self.id)

class Instagrams(db.Model):

    __tablename__ = "instagrams"

    id = db.Column(db.Integer, primary_key=True)
    keyword_id = db.Column(db.Integer, db.ForeignKey('keywords.id'), nullable=False)
    keyword = db.relationship('Keywords', backref='keywords')
    raw_id = db.Column(db.Integer, db.ForeignKey('raws.id'), nullable=False)
    raw = db.relationship('Raws', backref='raws')
    brand_id = db.Column(db.Integer, db.ForeignKey('brands.id'), nullable=False)
    brand = db.relationship('Brands')
    instagram_id = db.Column(db.String(255))
    instagram_user_id = db.Column(db.String(255))
    instagram_user_name = db.Column(db.String(255))
    instagram_followers_count = db.Column(db.Integer)
    instagram_media_url = db.Column(db.String(255))
    instagram_sentiment = db.Column(db.String(255)) # 0 negative, 1 neutral, 2 positive
    instagram_text  = db.Column(db.Text)
    instagram_lang  = db.Column(db.String(255))
    instagram_url  = db.Column(db.String(255))
    instagram_topics  = db.Column(db.String(255))
    tokenizer = db.Column(db.ARRAY)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return str(self.id)
