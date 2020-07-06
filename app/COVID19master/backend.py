import numpy as np
import pandas as pd
import time, os, json, copy

from app.COVID19master import global_var as gv
from app.COVID19master import COVID_model_colab as cov

def read_ABC(from_java):
    data = {'Date':{}, 'A':{}, 'B':{}, 'C':{}}
    policies = from_java['policy']
    for name, policy in policies.items():
        for plan, array in policy.items():
            data[plan][name] = array
    plans = ['A', 'B', 'C']
    policies = ['CR', 'CT', 'UT']
    dates = data['Date']['CT'] # hard coded
    days_per_tp = 7
    index = [0] + [i for i in dates for j in range(days_per_tp)]
    rl_input = {}
    for plan in plans:
        rl_input[plan] = pd.DataFrame(index=index, columns=policies)
        for policy, changes in data[plan].items():
            to_rl = [0]
            for change in changes:
                to_rl += [change] * days_per_tp
            rl_input[plan][policy] = to_rl
        rl_input[plan].iloc[0] = rl_input[plan].iloc[1].values
        rl_input[plan] = rl_input[plan].values
        if np.sum(rl_input[plan]==0) == len(rl_input[plan])*3:
            rl_input.pop(plan)
    return rl_input
    

# Funtion for one scenario analysis
def main_run(state, decision, T_max, uw=50, costs=[50,50,50], data=None,
             pre_data = None, heroku=False, max_time=25):
    path = os.getcwd()
    inv_dt = 10               # insert time steps within each day
    gv.setup_global_variables(state, inv_dt, path, heroku=heroku)
    gv.md_salary = uw
    gv.test_cost = costs
    gv.T_max = T_max
    # ^ set gloable variables
    timer, time_start = 0, time.time() # set timer and current time
    model = cov.CovidModel(data=data, heroku=heroku) # establish model
    i = 0 # set loop counter
    d_m = decision[i] # set current policy at time=now
    # while there time now < time end AND
    # while timer < max_time AND time_step is at the end of a day (aka no partial days)
    while model.t < model.T_total and (timer < max_time or i % model.inv_dt != 0):
        model.t += 1
        if model.t % 25 == 0: print('t', model.t, np.round(timer, 2))
        # ^ print progress
        if i % model.inv_dt == 0: # if next day, set policy for the new day
            d_m = decision[i//model.inv_dt]

        model.step(action_t = d_m) # run step
        i += 1  # move time
        timer = time.time() - time_start # update timer
    mod = model.t - model.d * model.inv_dt 
    date_range = pd.date_range(start= model.sim_start_day, periods= model.d, freq = 'D')
    # ^^ FROM XINMENG ... idk what this means
    # save results... this is used to restart a simulation on next loop
    dic = {'self.pop_dist_sim': model.pop_dist_sim[model.t- mod].tolist(),
           'self.num_diag': model.num_diag[model.t- mod].tolist(),
           'self.num_hosp': model.num_hosp[model.t- mod].tolist(),
           'self.num_dead': model.num_dead[model.t- mod].tolist(),
           'self.num_base_test': model.num_base_test[model.t- mod].tolist(),
           'self.num_uni_test': model.num_uni_test[model.t- mod].tolist(),
           'self.num_trac_test': model.num_trac_test[model.t-mod].tolist(),
           'self.tot_num_diag': model.tot_num_diag[model.t-mod],
           'self.tot_num_dead': model.tot_num_dead[model.t-mod],
           'self.tot_num_hosp': model.tot_num_hosp[model.t-mod],
           'self.rate_unemploy': model.rate_unemploy[model.t-mod],
           'self.next_start_day': date_range[-1].strftime("%m/%d/%Y"),
           'self.t': model.t}
    # get results for graphics on website
    output = model.op_ob.write_output(pre_results = gv.pre_results_df,
                                      date_range = date_range,
                                      pre_data = pre_data)
    remaining_decision = decision[i//model.inv_dt :] 
    # ^ cut the simulation policy for what still needs to be simulated
    is_complete = 'True' if model.T_total - model.t <= 2 else 'False'
    # ^ check if simulation is done
    results = {'pre_data':dic, 'to_java':output, 'remaining_decision':remaining_decision,
               'is_complete':is_complete, 'cost':costs, 'unemp':uw}
    results = prep_results_for_java(results)
    # ^^ prep results for java
    return results


def prep_results_for_java(results):
    results = copy.deepcopy(results)
    results['is_complete'] = str(results['is_complete'])
    if results['to_java'] == None:
        results['to_java'] = json.dumps(results['to_java'])
    else:
        df1, df2, df3, df4, df5 = results['to_java']
        temp = {'VSL':df1,'Summary':df5,'Testing':df3,
                'Decision Choice':df4, 'Unemployment':df2}
        temp['Summary']['Date'] = temp['Summary'].index.astype(str)
        for k,v in temp.items():
            temp[k].index = temp[k].index.astype(str)
        results['to_java'] = {k : json.dumps(v.astype(str).to_dict('index')) for k,v in temp.items()}
    results['remaining_decision'] = json.dumps(results['remaining_decision'].tolist())
    results['cost'] = json.dumps(results['cost'])
    results['unemp'] = json.dumps(results['unemp'])
    results['pre_data'] = json.dumps(results['pre_data'])
    return results

def prep_input_for_python(results):
    results = copy.deepcopy(results)
    for plan, instructions in results.items():
        if plan in ['A', 'B', 'C']:
            if instructions['to_java'] != 'null':
                instructions['to_java'] = [pd.read_json(v).T for v in instructions['to_java'].values()]
            else:
                instructions['to_java'] = None
            instructions['remaining_decision'] = np.array(json.loads(instructions['remaining_decision']))
            instructions['pre_data'] = json.loads(instructions['pre_data'])
            instructions['cost'] = json.loads(instructions['cost'])
            instructions['unemp'] = json.loads(instructions['unemp'])
            results[plan] = instructions
    return results