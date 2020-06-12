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
