# -*- encoding: utf-8 -*-

from app.blueprints.interface import blueprint
from flask import render_template, redirect, url_for
from flask_login import login_required, current_user
from app.extensions import login_manager, db

from sqlalchemy.exc import IntegrityError

from jinja2 import TemplateNotFound
from app.blueprints.interface.forms import AddBrand, AddKeyword, AddPlatform
from app.blueprints.interface.models import Brands, Keywords, Platforms

from sqlalchemy import event
from datetime import datetime


## Main App


#===BRAND===

@blueprint.route('/create-demo-data', methods=['GET'])
def create_demo_data():
    # this should probably better be a listen_for after_create in the blueprint
    now = datetime.now()
    db.session.add(Platforms(platform_name='Twitter', created_at=now))
    db.session.add(Platforms(platform_name='Instagram', created_at=now))
    db.session.add(Brands(brand_name='Minecraft', created_at=now))
    db.session.add(Keywords(keyword_name='Bordeaux', brand_id=1 , created_at=now))
    db.session.add(Keywords(keyword_name='Vin', brand_id=1 , created_at=now))    

    try:
        db.session.commit()
    except IntegrityError as err:
        db.session.rollback()
        if "duplicate key" in str(err):
            return 'error demo already created'
        else:
            return 'error'
    return 'Created'

@blueprint.route('/create-brand', methods=['GET', 'POST'])
@login_required
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

@blueprint.route('/brand/<brand_name>')
def brand_stats(brand_name):
    return render_template('stats/stats.html', brand_name=brand_name)

#===Keyword===
@blueprint.route('/create-platform', methods=['GET', 'POST'])
@login_required
def create_Platform():

    add_platform_form =  AddPlatform()
    if add_platform_form.validate_on_submit():

        form_platform = Brands()
        add_platform_form.populate_obj(form_platform)

        db.session.add(form_platform)
        try:
            db.session.commit()
        except IntegrityError as err:
            db.session.rollback()
            if "duplicate key" in str(err):
                return render_template( 'platform/create-platform.html', error='Platform already Exists', form=add_platform_form)
            else:
                return render_template( 'platform/create-platform.html', error='Unknown error adding Platform please Retry', form=add_platform_form)

        return render_template( 'platform/create-platform.html', success='platform created ! go to <platform>', form=add_platform_form)
    return render_template('platform/create-platform.html',form=add_platform_form)

#===Platform===
@blueprint.route('/create-keyword', methods=['GET', 'POST'])
@login_required
def create_keyword():

    add_keyword_form =  AddKeyword()
    if add_keyword_form.validate_on_submit():
        form_keyword = Keywords()
        add_keyword_form.populate_obj(form_keyword)
        db.session.add(form_keyword)
        db.session.commit()
        return render_template( 'keyword/create-keyword.html', success='Keyword created ! go to <keyword>', form=add_keyword_form)
    return render_template('keyword/create-keyword.html',form=add_keyword_form)
