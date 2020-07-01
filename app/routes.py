from flask import (Blueprint, flash, redirect, render_template, request, 
                   url_for, jsonify, Response, send_file)
# from app import db
# from app.models import User
import pandas as pd
from app.COVID19master import COVID_model
from app.COVID19master import COVID_model_colab
from app.COVID19master import read_policy_mod
import numpy as np
import time
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
    #return render_template('input.html')
    return render_template('policy_builder.html')

@bp.route('/simResult', methods=('GET', 'POST'))
def render_result():
    return render_template('simResult.html')

@bp.route('/input/download_newfile')
def download_newfile():
    path = 'policy_example.xlsx'
    return send_file(path, attachment_filename='new_test.xlsx', as_attachment=True)

# @bp.route('/calibrate_model', methods=('GET','POST'))
# def calibrate_model():
#     get = request.get_json()[0] # retrieve input data from ajax request
#     to_df = {}
#     state = get['state']
#     for i,v in enumerate(get['rl_input']):
#         to_df[i] = v
#     df = pd.DataFrame.from_dict(to_df,orient='index')
#     rl_input = read_policy_mod.read_policy(df)
#     heroku = False
#     if len(os.getcwd()) < 25:
#         heroku = True
#     covid_model = COVID_model.run_calibration(state='NY', decision=rl_input, heroku=heroku)
#     results = COVID_model.run_simulation(covid_model, state = "NY", decision = rl_input, heroku=heroku)
#     results['Summary']['Date'] = results['Summary'].index.astype(str)
#     for k,v in results.items():
#         results[k].index = results[k].index.astype(str)
#     to_java = {k : json.dumps(v.astype(str).to_dict('index')) for k,v in results.items()}
#     return jsonify(status='success', data=to_java)

@bp.route('/prep_sim', methods=('GET','POST'))
def prep_sim():
    get = request.get_json() # retrieve input data from ajax request
    if get['new'] == 'True':
        rl_input = read_policy_mod.read_ABC(get)
        results = {plan:{'is_complete':'False',
                         'remaining_decision':decision,
                         'to_java':None,
                         'pre_data':None} for plan, decision in rl_input.items()}
    else:
        results = COVID_model_colab.prep_input_for_python(get) # need to parse to get in python format    
        print(results['A']['pre_data'].keys())
        print(results['A']['pre_data']['self.next_start_day'])
    heroku = False if len(os.getcwd()) > 25 else True
    max_time=15
    stop=False
    for plan, instructions in results.items():
        if type(instructions) == dict:
            if instructions['is_complete'] == 'False' and stop == False:
                decision = instructions['remaining_decision']
                T_max = decision.shape[0]
                data = instructions['to_java']
                pre_data = instructions['pre_data']
                output = COVID_model_colab.main_run(State='NY', decision=decision,
                                                     uw=50, costs= [50, 50, 50], T_max=T_max,
                                                     data=pre_data, pre_data=data,
                                                     heroku=heroku, max_time=max_time)
                stop = True
                results[plan] = output
            else:
                results[plan] = COVID_model_colab.prep_results_for_java(results[plan])
    if all([v['is_complete'] == 'True' for k,v in results.items() if type(v) == dict]):
        status = 'Finished'
    else:
        status = 'Not Finished'
    results['status'] = status
    results['new'] = 'False'
    return jsonify(status='success', data=results)

# @bp.route('/prep_sim_old', methods=('GET','POST'))
# def prep_sim_old():
#     get = request.get_json() # retrieve input data from ajax request
#     rl_input = read_policy_mod.read_ABC(get)
#     state = get['state']
#     heroku = False
#     timer = time.time()
#     if len(os.getcwd()) < 25:
#         heroku = True
#     results = {}
#     for plan, decision in rl_input.items(): 
#         results[plan] = ''
#         output = COVID_model.run_calibration(state='NY',
#                                                   decision=decision,
#                                                   heroku=heroku)
#         # covid_model = COVID_model.run_calibration(state='NY',
#         #                                           decision=decision,
#         #                                           heroku=heroku)
#         # output = COVID_model.run_simulation(covid_model,
#         #                                            state = "NY",
#         #                                            decision = decision,
#         #                                            heroku=heroku)
#         output['Summary']['Date'] = output['Summary'].index.astype(str)
#         for k,v in output.items():
#             output[k].index = output[k].index.astype(str)
#         results[plan] = {k : json.dumps(v.astype(str).to_dict('index')) for k,v in output.items()}
#     to_java = results
#     time_now = time.time()
#     if time_now - timer < 10000:
#         to_java['finished'] = 'False'
#         to_java = {'finished':'False'}
#     return jsonify(status='success', data=to_java)


@bp.route('/continue_sim', methods=('GET','POST'))
def continue_sim():
    get = request.get_json() # retrieve input data from ajax request
    get['finished'] ='true'
    print('hello')
    return jsonify(status='success', data=get)
