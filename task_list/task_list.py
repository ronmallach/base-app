from flask import (
    Blueprint, flash, redirect, render_template, request, url_for, jsonify
)
from task_list import db
from task_list.models import Task
import pandas as pd
#from app.load import load
# from app import app, db
# from werkzeug.urls import url_parse
import json
import os


bp = Blueprint('task_list', __name__)


# @app.route('/')
# @app.route('/index')
# @login_required
@bp.route('/', methods=('GET', 'POST'))
def index():
    return render_template('index.html')


# @app.route('/sunburst')
# @login_required
@bp.route('/sunburst', methods=('GET', 'POST'))
def sunburst():
    return render_template('sunburst.html')

# @app.route('/line')
# @login_required
@bp.route('/line', methods=('GET', 'POST'))
def line():
    return render_template('line.html')

# @app.route('/dataInput')
# @login_required
@bp.route('/dataInput', methods=('GET', 'POST'))
def dataInput():
    return render_template('dataInput.html')

# @app.route('/calender')
# @login_required
@bp.route('/calender', methods=('GET', 'POST'))
def calender():
    return render_template('calender.html')

# @app.route('/goMap')
# @login_required
@bp.route('/goMap', methods=('GET', 'POST'))
def goMap():
    data = {1:3, 5:3}
    print(data)
    return render_template('goMap.html', data=data)


# @app.route('/login', methods=['GET', 'POST'])
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
#             next_page = url_for('index')
#         return redirect(next_page)
#     return render_template('login.html', title='Sign In', form=form)

# @app.route('/logout')
# def logout():
#     logout_user()
#     return redirect(url_for('index'))

# @app.route('/register', methods=['GET', 'POST'])
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

@bp.route('/load_map', methods = ['POST'])
def loadMap():
    data = json.load(open('task_list\data\counties-albers-10m.json'))
    covid = json.load(open('task_list\data\covid-us-counties.json'))
    return jsonify(status='success', data=data, covid=covid)

# @app.route('/get_subcat_loc', methods = ['POST'])
# def load_data():
#     #trans, income, budget, goal = load.load_new()
#     user = User.query.filter_by(username=current_user.username).first()
#     if user.expense != None:
#         trans = pd.read_json(user.expense, orient='index')
#         if len(trans) == 0:
#             trans, income, budget, goal = load.initialize()
#         else:
#             trans.Date = trans.Date.astype(str)
#             income = pd.read_json(user.income, orient='index')
#             income.Date = income.Date.astype(str)
#             budget = pd.read_json(user.budget, orient='index')
#             goal = pd.read_json(user.goal, orient='index')
#             goal.Date = goal.Date.astype(str)
#     else:
#         trans, income, budget, goal = load.initialize()
#     business, cat, subcat, summary = load.go(t=trans, i=income, java=True)
#     data = {'expense': json.dumps(trans.to_dict('index')),
#             'income': json.dumps(income.to_dict('index')),
#             'budget':json.dumps(budget.to_dict('index')),
#             'goal':json.dumps(goal.to_dict('index')),
#             'Summary':summary,
#             'stackCat':cat,
#             'stackSub':subcat}
#     return jsonify(status='success', data=data)

# @app.route('/save_new_data', methods = ['POST'])
# def save_data():
#     get = request.get_json() # retrieve input data from ajax request
#     trans, income, budget, goal = load.update(get)
#     user = User.query.filter_by(username=current_user.username).first()
#     user.expense = json.dumps(trans.to_dict('index'))
#     user.income = json.dumps(income.to_dict('index'))
#     user.budget = json.dumps(budget.to_dict('index'))
#     user.goal = json.dumps(goal.to_dict('index'))
#     db.session.commit()
#     business, cat, subcat, summary = load.go(trans, income, java=True)
#     data = {'expense': json.dumps(trans.to_dict('index')),
#             'income': json.dumps(income.to_dict('index')),
#             'budget':json.dumps(budget.to_dict('index')),
#             'goal':json.dumps(goal.to_dict('index')),
#             'Summary':summary,
#             'stackCat':cat,
#             'stackSub':subcat}
#     return jsonify(status='success', data=data)

