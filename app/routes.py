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


@bp.route('/download')
def download_file():
	path = "dummy.xlsx"
	return send_file(path, as_attachment=True)


ALLOWED_EXTENSIONS = {'csv', 'xls', 'xlsx'}
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = file.filename
            UPLOAD_FOLDER = '/uploads/'
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            return redirect(url_for('/', filename=filename))


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
