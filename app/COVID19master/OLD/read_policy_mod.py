# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np

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
    