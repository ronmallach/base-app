from flask import (
    Blueprint, flash, redirect, render_template, request, url_for,
    jsonify, Response, send_file
)

from app import db
from app.models import User

import pandas as pd
from app.COVID19master import COVID_model
from app.COVID19master import read_policy_mod
import numpy as np
# import app.COVID_model
# import app.read_policy_mod
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
def render_input():
    return render_template('input.html')

@bp.route('/input/download_newfile')
def download_newfile():
    print('hello')
    path = 'policy_example.xlsx'
    return send_file(path, attachment_filename='new_test.xlsx', as_attachment=True)

@bp.route('/calibrate_model', methods=('GET','POST'))
def calibrate_model():
    get = request.get_json() # retrieve input data from ajax request
    to_df = {}
    for i,v in enumerate(get):
        to_df[i] = v
    df = pd.DataFrame.from_dict(to_df,orient='index')
    rl_input = read_policy_mod.read_policy(df)
    cwd = os.getcwd()
    #excel1= os.path.join(cwd,'app\\COVID19master\\data\\COVID_input_parameters.json')
    #path = 'policy_example.xlsx'
    #excel1 = os.path.join(cwd,'COVID19master/data/COVID_input_parameters.json')
    #test = json.load(open(excel1))
    what = os.listdir(cwd)
    #q_mat_blank = pd.read_excel(path, sheet_name='Decision')
    # results = COVID_model.run_simulation(state = "NY", decision = rl_input)
    # for k,v in results.items():
    #     results[k].index = results[k].index.astype(str)
    # to_java = {k : json.dumps(v.astype(str).to_dict('index')) for k,v in results.items()}
    #to_java = json.dumps({})
    to_java = json.dumps({0: cwd, 1:what,}) #2:what})
    return jsonify(status='success', data=to_java)

# @bp.route('/login', methods=['GET', 'POST'])
# def login():
#     if current_user.is_authenticated:
#         return redirect(url_for('index'))
#     form = LoginForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(username=form.username.data).first()
#         if user is None or not user.check_password(form.password.data):
#             flash('Invalid username or password')
#             return redirect(url_for('login'))
#         login_user(user, remember=form.remember_me.data)
#         next_page = request.args.get('next')
#         if not next_page or url_parse(next_page).netloc != '':
#              next_page = url_for('index')
#         return redirect(next_page)
#     return render_template('login.html', title='Sign In', form=form)

# @bp.route('/logout')
# def logout():
#     logout_user()
#     return redirect(url_for('index'))

# @bp.route('/register', methods=['GET', 'POST'])
# def register():
#     if current_user.is_authenticated:
#         return redirect(url_for('index'))
#     form = RegistrationForm()
#     if form.validate_on_submit():
#         user = User(username=form.username.data, email=form.email.data)
#         user.set_password(form.password.data)
#         db.session.add(user)
#         db.session.commit()
#         flash('Congratulations, you are now a registered user!')
#         return redirect(url_for('index'))
#     return render_template('register.html', title='Register', form=form)
