# -*- encoding: utf-8 -*-

from app.blueprints.interface import blueprint
from flask import render_template, redirect, url_for
from flask_login import login_required, current_user
from app.extensions import login_manager, db

from sqlalchemy.exc import IntegrityError

from jinja2 import TemplateNotFound
from app.blueprints.interface.forms import AddBrand, AddKeyword
from app.blueprints.interface.models import Brands, Keywords

## Main App

@blueprint.route('/create-brand', methods=['GET', 'POST'])
#@login_required
def create_brand():

    add_brand_form =  AddBrand()
    if add_brand_form.validate_on_submit():

        form_brands = Brands()
        add_brand_form.populate_obj(form_brands)

        db.session.add(form_brands)
        try:
            db.session.commit()
        except IntegrityError as err:
            db.session.rollback()
            if "duplicate key" in str(err):
                return render_template( 'brand/create-brand.html', error='Brand already Exists', form=add_brand_form)
            else:
                return render_template( 'brand/create-brand.html', error='Unknown error adding Brand please Retry', form=add_brand_form)

        return render_template( 'brand/create-brand.html', success='Brand created ! go to <brand>', form=add_brand_form)
    return render_template('brand/create-brand.html',form=add_brand_form)


@blueprint.route('/create-keyword', methods=['GET', 'POST'])
#@login_required
def create_keyword():

    add_keyword_form =  AddKeyword()
    if add_keyword_form.validate_on_submit():
        form_keyword = Keywords()
        add_keyword_form.populate_obj(form_keyword)
        db.session.add(form_keyword)
        db.session.commit()
        return render_template( 'keyword/create-keyword.html', success='Keyword created ! go to <keyword>', form=add_keyword_form)
    return render_template('keyword/create-keyword.html',form=add_keyword_form)
