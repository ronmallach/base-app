# -*- coding: utf-8 -*-

import pandas as pd
from math import isnan
import numpy as np

def read_policy(df):
    print(df)
    print(df.loc[:, df.columns.str.contains('Startday')].replace('',np.nan).replace(' ',np.nan))
    look_startday = df.loc[:, df.columns.str.contains('Startday')].replace('',np.nan).astype(float)
    max_day = int(look_startday.max().max())
    new_df = pd.DataFrame(index=[i for i in range(max_day)], columns=[1,2,3])
    for col in new_df:
        day_col = df.iloc[:, col*2-2].replace('',np.nan)
        pol_col = df.iloc[:, col*2-1].replace('',np.nan)
        data = []
        changes = sum(day_col.isna() == False)-1
        for change in range(changes):
            data += [float(pol_col.iloc[change])] * (int(day_col.iloc[change+1])-int(day_col.iloc[change]))
        new_df[col] = data
    policy = new_df.values
    return policy


def read_ABC(from_java):
    data = {'Date':{}, 'A':{}, 'B':{}, 'C':{}}
    state = from_java['state']
    policies = from_java['policy']
    for name, policy in policies.items():
        for plan, array in policy.items():
            data[plan][name] = array
    plans = ['A', 'B', 'C']
    policies = ['CT', 'UT', 'CR']
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
    