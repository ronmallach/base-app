from flask import (
    Blueprint, flash, redirect, render_template, request, url_for,
    jsonify, Response, send_file
)
from app import db
from app.models import User
import pandas as pd
#from app.load import load
# from app import app, db
# from werkzeug.urls import url_parse
#from app.forms import LoginForm, RegistrationForm
#from flask_login import current_user, login_user, logout_user, login_required
import json
import os

bp = Blueprint('blueprint', __name__)

# @app.route('/')
# @app.route('/index')
# @login_required
@bp.route('/', methods=('GET', 'POST'))
def index():
    return render_template('index.html')

@bp.route('/input', methods=('GET', 'POST'))
def input():
    return render_template('input.html')

@bp.route('/input/download')
def download_file():
	path = "dummy.xlsx"
	return send_file(path, attachment_filename='test.xlsx', as_attachment=True)

@bp.route('/calibrate_model', methods=('GET','POST'))
def calibrate_model():
    get = request.get_json() # retrieve input data from ajax request
    print(get)
    return jsonify(status='success', data=get)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
             next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('index'))
    return render_template('register.html', title='Register', form=form)
