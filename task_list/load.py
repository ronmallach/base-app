import pandas as pd
import numpy as np
import datetime as dt
import json
#from app.models import User
#from flask_login import current_user
#from app import app, db


def load_new():
    transaction = pd.read_pickle('app/data/trans.pkl')
    income = pd.read_pickle('app/data/income.pkl')
    budget = pd.read_pickle('app/data/budget.pkl')
    goals = pd.read_pickle('app/data/goal.pkl')
    return transaction, income, budget, goals



trans, income, budget, goal = load_new()

#user = User.query.filter_by(username=current_user.username).first()
#
#trans = user.expense
#income = user.income
#budget = user.budget
#goal = user.goal


def go(t, i, java=True):
    mid = {}
    top = {}
    t.Amount = np.round(t.Amount.astype(float),2)
    i.Amount = np.round(i.Amount.astype(float),2)
    categories = ['Shopping', 'Other', 'Bills & Utilities', 'Auto & Commuting',
                  'Entertainment & Travel', 'Food & Drinks']
    for cat in categories:
        b = t[t.Category == cat]
        top[cat] = list(b.Business.unique())
    for subcat in t.SubCategory.unique():
        b = t[t.SubCategory == subcat]
        mid[subcat] = list(b.Business.unique())
    if 'To Savings' not in mid.keys():
        mid['To Savings'] = []
    summary_columns = ['Needs', 'Wants' , 'Spent', 'Income', 'Checking', 'Savings', 'Total']
    mindate = min(t.Date.min(), i.Date.min())
    maxdate = max(t.Date.max(), i.Date.max())
    gt = t.groupby(['Date', 'Business']).sum().unstack(fill_value=0)
    gt.columns = [c[1] for c in gt.columns]
    gt.index = [pd.Timestamp(ind) for ind in gt.index]
    it = i.groupby(['Date', 'Location']).sum().unstack(fill_value=0)
    it.columns = [c[1] for c in it.columns]
    it.index = [pd.Timestamp(ind) for ind in it.index]
    dates = pd.date_range(mindate, maxdate)
    by_bus = gt.reindex(dates, fill_value=0.0)
    new_income = it.reindex(dates, fill_value=0.0).sum(1)
    cb = by_bus
    cs = pd.DataFrame(0.0, dates, columns=list(mid.keys()))
    cc = pd.DataFrame(0.0, dates, columns=list(top.keys()))
    summary = pd.DataFrame(0.0, dates, columns=summary_columns)
    for subcat in mid.keys():
        cs[subcat] = cb[mid[subcat]].sum(1)
    for cat in top.keys():
        cc[cat] = cb[top[cat]].sum(1)
    needs = ['Auto & Commuting', 'Bills & Utilities']
    wants = ['Entertainment & Travel','Food & Drinks','Other','Shopping']
    summary.Needs = cc[needs].sum(1)
    summary.Wants = cc[wants].sum(1) - cs['To Savings']
    summary.Spent = summary.Needs + summary.Wants
    summary.Income = new_income
    summary.Savings = cs['To Savings']
    summary.Checking = summary.Income - summary.Spent - summary.Savings
    summary.Total = summary.Checking + summary.Savings
    summary = summary.cumsum()
    if java == True:
        dates = dates.astype(str)
        cb = post_process(cb.cumsum(), dates)
        cc = post_process(cc.cumsum(), dates)
        cs = post_process(cs.cumsum(), dates)
        summary = post_process(summary, dates)
    return cb,cc,cs,summary
# Start Here    
    
def post_process(df, dates):
    df = df.reset_index(drop=True)
    df.insert(0, 'Date', dates)
    javaReady = json.dumps(df.to_dict('index'))
    return javaReady

#def update(get, trans, income, budget, goal):
def update(get):
    t_columns = ['Date', 'Category', 'SubCategory', 'Location', 'Business', 'Amount']
    i_columns = ['Date', 'Location', 'Amount']
    g_columns = ['Date', 'Amount', 'Comment']
    b_columns = ['Category', 'Percentage']
    categories = ['Shopping', 'Other', 'Bills & Utilities', 'Auto & Commuting',
                  'Entertainment & Travel', 'Food & Drinks']
    trans_data = get[0]['expense']
    income_data = get[0]['income']
    budget_data = get[0]['budget']
    goal_data = get[0]['goal']
    next_trans_index = 0
    next_income_index = 0
    next_budget_index = 0
    next_goal_index = 0
    new_trans = pd.DataFrame(columns=t_columns)
    new_income = pd.DataFrame(columns=i_columns)
    new_budget = pd.DataFrame(columns=b_columns)
    new_goal = pd.DataFrame(columns=g_columns)
    for t in trans_data:
        fix_cat = t['Category'].replace('amp;','')
        fix_sc = t['SubCategory'].replace('amp;','')
        fix_biz = t['Business'].replace('amp;','')
        new_val = [t['Date'], fix_cat, fix_sc, t['Location'], fix_biz, np.round(float(t['Amount']),2)]
        new_trans.loc[next_trans_index] = new_val
        next_trans_index += 1
    for i in income_data:
        new_income.loc[next_income_index] = [i['Date'], i['Location'], np.round(float(i['Amount']))]
        next_income_index += 1
    for b in budget_data:
        fix_cat = b['Category'].replace('amp;','')
        new_budget.loc[next_budget_index] = [b['Category'], b['Percentage']]
        next_budget_index += 1
    for g in goal_data:
        new_goal.loc[next_goal_index] = [g['Date'], np.round(float(g['Amount'])), g['Comment']]
        next_goal_index += 1
    new_trans = new_trans.sort_values('Date')
    new_income = new_income.sort_values('Date')
    new_goal = new_goal.sort_values('Date')
    save(new_trans, 'trans')
    save(new_income, 'income')
    save(new_budget, 'budget')
    save(new_goal, 'goal')
    return new_trans, new_income, new_budget, new_goal

def save(df, name):
    df.to_pickle('app/data/' + name + '.pkl')

def initialize_budget(trans):
    categories = trans.Category.unique()
    budget = {}
    for i, category in enumerate(categories):
        budget[i] = {'Category':category, 'Percentage':0}
    budget = pd.DataFrame().from_dict(budget, 'index')
    #save(budget, 'budget')
    return budget
    
def initialize_goals():
    goal = pd.DataFrame(columns=['Date', 'Amount', 'Comment'])
    #save(goal, 'goal')
    return goal
    
def initialize():
    t_columns = ['Date', 'Category', 'SubCategory', 'Location', 'Business', 'Amount']
    i_columns = ['Date', 'Location', 'Amount']
    categories = ['Shopping', 'Other', 'Bills & Utilities', 'Auto & Commuting',
                  'Entertainment & Travel', 'Food & Drinks']
    start_trans = [[str(dt.date.today()), 'N/A', 'N/A', 'N/A', 'N/A', 0]]
    start_income = [[str(dt.date.today()), 'N/A', 0]]
    trans = pd.DataFrame(start_trans, index=[0], columns=t_columns)
    income = pd.DataFrame(start_income, index=[0], columns=i_columns)
    budget = {}
    for i, category in enumerate(categories):
        budget[i] = {'Category':category, 'Percentage':0}
    budget = pd.DataFrame().from_dict(budget, 'index')
    goal = pd.DataFrame(columns=['Date', 'Amount', 'Comment'])
    return trans, income, budget, goal
    
