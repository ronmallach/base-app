from flask import (Blueprint, flash, redirect, render_template, request,
                   url_for, jsonify, Response, send_file)
# from app.COVID19master import COVID_model_colab
# from app.COVID19master import read_policy_mod
from app.COVID19master import backend
import os


bp = Blueprint('blueprint', __name__)


# @bp.route('/', methods=('GET', 'POST'))
# def index():
#     return render_template('index.html')

@bp.route('/', methods=('GET', 'POST'))
def index():
    #return render_template('input.html')
    return render_template('policy_builder.html')


@bp.route('/input/download_newfile')
def download_newfile():
    path = 'policy_example.xlsx'
    return send_file(path, attachment_filename='new_test.xlsx', as_attachment=True)


@bp.route('/prep_sim', methods=('GET','POST'))
def prep_sim():
    get = request.get_json() # retrieve input data from ajax request
    # if this is the first time the simulation is being run through, prep the
    # data from the front end... see line 91 where this is set as False.
    if get['new'] == 'True':
        print([int(cost) for cost in get['cost']])
        rl_input = backend.read_ABC(get)
        # transform user inputs... will return
        results = {plan:{'is_complete':'False',
                         'remaining_decision':decision,
                         'to_java':None,
                         'pre_data':None,
                         'cost':[int(cost) for cost in get['cost']],
                         'prop':int(get['UW'])} for plan, decision in rl_input.items()}
    else:
    # else, if this is NOT the first time the prep_sim function is called,
    # take the partially completed simulation data and prep it.
        results = backend.prep_input_for_python(get)
    heroku = False if len(os.getcwd()) > 25 else True # set the paths
    max_time = 15 # passed to simulation as the max time to run for
    stop=False # condition to make sure simulation loop does not start another plan
    for plan, instructions in results.items(): # for plan in [A,B,C]
        if type(instructions) == dict:
            # if simulation isn't done, and stop condition not set yet
            if instructions['is_complete'] == 'False' and stop == False:
                decision = instructions['remaining_decision']
                T_max = decision.shape[0]
                data = instructions['to_java']
                pre_data = instructions['pre_data']
                costs = instructions['cost']
                uw = instructions['prop']
                # ^ make parameters
                output = backend.main_run(state='UMASS', decision=decision,
                                          uw=1, costs=costs, T_max=T_max,
                                          data=pre_data, pre_data=data,
                                          heroku=heroku, max_time=max_time)
                # ^ run simulation... will end after 15 seconds, or if simulation
                # of current plan is completed
                stop = True # set stop conditions
                results[plan] = output # save results
            else:
                # if plan has already been simulated, prep back for java
                results[plan] = backend.prep_results_for_java(results[plan])
    # check to see if all plans are simulated
    if all([v['is_complete'] == 'True' for k,v in results.items() if type(v) == dict]):
        status = 'Finished'
    else:
        status = 'Not Finished'
    results['status'] = status # set status
    results['new'] = 'False' # set status
    return jsonify(status='success', data=results)
