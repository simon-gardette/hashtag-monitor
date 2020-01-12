# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

from flask_wtf import FlaskForm
from wtforms import Form, TextField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Email, DataRequired, Length
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from app.blueprints.interface.models import Brands
from sqlalchemy import text


class AddBrand(FlaskForm):
    brand_name     = TextField('Brand Name', validators=[DataRequired()])

class AddPlatform(FlaskForm):
    platform_name     = TextField('Platform Name', validators=[DataRequired()])

class AddKeyword(FlaskForm):
    def brand_query():
        return Brands.query.order_by(text('brand_name asc')).all()

    brand = QuerySelectField('Select Existing Brand', query_factory=brand_query, validators=[DataRequired()], get_label='brand_name',  blank_text="Click to select")
    keyword_name   = TextField('Keyword', id='keyword_create', validators=[DataRequired()], )

# def brands_query(request, id):
#     brands = Brands.query.get(id)
#     form = AddKeyword(request.POST, obj=brand)
#     form.group_id.choices = [(g.id, g.brand_name) for g in Group.query.order_by('brand_name')]
