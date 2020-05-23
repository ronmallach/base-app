import pandas as pd
import datetime
import numpy as np

def setup_global_variables(state, beta_pre_sd, beta_post_sd, inv_dt1, T_max_, lead_time_, time_unit_, beta_user_defined_):
    ##### do not change ######
    global tot_risk
    tot_risk = 2

    global tot_age
    tot_age = 101
    ##### do not change ######

    ##### user defined input #######
    global enter_state
    enter_state = state

    global beta_before_sd 
    beta_before_sd  = beta_pre_sd

    global beta_after_sd
    beta_after_sd = beta_post_sd

    global T_max
    T_max = T_max_

    global inv_dt
    inv_dt = inv_dt1

    global dt
    dt = 1/inv_dt

    global lead_time
    lead_time = lead_time_ 

    global time_unit
    time_unit = time_unit_ 

    global beta_user_defined
    beta_user_defined = beta_user_defined_
    ##### user defined input #######

    ##### read input #######
    sim_result = read_input(state = enter_state)

    begin_simul_rl_date = sim_result[2]

    global days_of_simul_pre_sd
    days_of_simul_pre_sd = int(sim_result[3])

    global days_of_simul_post_sd
    days_of_simul_post_sd = int(sim_result[4])

    global dry_run_end_diag
    dry_run_end_diag = int(sim_result[5])

    global symp_hospitalization_v
    symp_hospitalization_v = sim_result[6]

    global percent_dead_recover_days_v
    percent_dead_recover_days_v = sim_result[7]

    global pop_dist_v
    pop_dist_v = sim_result[8]

    global input_list_const_v # dataframe
    input_list_const_v = sim_result[9]
    
    global Q
    Q = sim_result[10]

    global rates_indices
    rates_indices = reading_indices(Q)

    global diag_indices
    diag_indices = diag_indices_loc(Q)

    global md_salary
    md_salary = 105.80  # median salary for unemployed

    rl_result = read_RL_inputs(state = enter_state, start_rl_sim_date = begin_simul_rl_date)

    global VSL
    VSL = rl_result[0]

    global lab_for
    lab_for = rl_result[1]

    global K_val
    K_val = rl_result[2]

    global A_val
    A_val = rl_result[3]

    global h_val
    h_val = rl_result[4]

    global init_unemploy
    init_unemploy = rl_result[5]
    


# Function to reading the following data files

# input.xlsx - has all the hospitalization, death and recovery data 
# actual_valid_data.xlsx - has all the states daily data
# sd_date.xlsx - has the start and end dates of social distancing protocal beginning and ending
# pop_dist - has the population distribution of susceptible in all states with age and risk group classification
# COVID_input_parameters.xlsx - has the initial q mat with 1's where rates are applicable and inital parameter values that need to be kept constant over time

# Input parameters for this function
# enter_state = two letter abbreviation of the state you want to model

def read_input(state):
    excel1= 'data/input.xlsx' 
    symp_hospitalization = pd.read_excel(excel1, sheet_name='symp_hospitalization') 
    percent_dead_recover_days = pd.read_excel(excel1, sheet_name='percent_dead_recover_days') 
    
    excel3 = 'data/actual_valid_data.xlsx'
    raw_valid_data = pd.read_excel(excel3, sheet_name='Sheet1')
    raw_valid_data_v = raw_valid_data.values

    excel4 = 'data/sd_date.xlsx'
    sd_date = pd.read_excel(excel4, sheet_name='Sheet1') 
    sd_date_v = sd_date.values 

    excel2 = 'data/pop_dist.xlsx'

    '''
    states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA", 
          "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", 
          "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", 
          "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", 
          "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]
    '''

    state_index = np.where(raw_valid_data_v==state)
    valid_data_v = raw_valid_data_v[state_index[0]]
    #valid_data_v_nan = np.nan_to_num(valid_data_v)
    
    df2 = pd.DataFrame(valid_data_v)


    # The beginning date where the number of infections exceed 0
    final_simul_start_date = valid_data_v[max(np.where(valid_data_v[:,2] > 0)[0]), 0]
    final_simul_start_date = str(final_simul_start_date)
    d1 = datetime.datetime.strptime(final_simul_start_date, '%Y%m%d')

    # The ending date where the number of infections exceed 0
    final_simul_end_date = valid_data_v[min(np.where(valid_data_v[:,2] > 0)[0]), 0]
    final_simul_end_date = str(final_simul_end_date)
    d2 = datetime.datetime.strptime(final_simul_end_date, '%Y%m%d')

    # Min number of infections that need to be diagnosed for dry run to end
    dry_run_end_diag = valid_data_v[max(np.where(valid_data_v[:,2] > 0)[0]), 2] 

    # The date where social distancing begins in the state
    sd_start_date_state = str(sd_date_v[np.where(sd_date_v == state)[0][0],1])
    sd_start_date_state = str(datetime.datetime.strptime(sd_start_date_state, "%Y-%m-%d %H:%M:%S"))
    d4= datetime.datetime.strptime(sd_start_date_state, '%Y-%m-%d %H:%M:%S')

    # Does not include one day 
    #(for NY from 03-04 to 03-22 it is 19 days but this doesnt include 03-22, only counts til 03-20)

    # The days before social distancing was introduced
    days_of_simul_pre_sd = (abs(d4 - d1).days)

    # The days after social distancing was introduced 
    days_of_simul_post_sd = (abs(d4 - d2).days)+1
    
    #days_of_simul = np.where(valid_data_v[:,2] > 0).shape[0]

    # writer.save()

    pop_dist = pd.read_excel(excel2, sheet_name = state) 
               
    excel5 = 'data/COVID_input_parameters.xlsx'
    input_list_const = pd.read_excel(excel5, sheet_name = 'input_list_const', index_col = 0) 

    q_mat_blank = pd.read_excel(excel5, sheet_name = 'q-mat_blank') 
    
    symp_hospitalization_v = symp_hospitalization.values.reshape((symp_hospitalization.shape))
    percent_dead_recover_days_v = percent_dead_recover_days.values.reshape((percent_dead_recover_days.shape))
    pop_dist_v = pop_dist.values.reshape((pop_dist.shape))
    # input_list_const_v = input_list_const.values
    q_mat_blank_v = q_mat_blank.values
    
    begin_simul_rl_date = str(valid_data_v[min(np.where(valid_data_v[:,2] > 0)[0]), 0])
    
    return (final_simul_start_date, sd_start_date_state, begin_simul_rl_date, days_of_simul_pre_sd, 
            days_of_simul_post_sd, dry_run_end_diag, symp_hospitalization_v, percent_dead_recover_days_v, 
            pop_dist_v, input_list_const, q_mat_blank_v, df2)
    
# Returns 12 values 
# [0] = final_simul_start_date - the day when simulation begins, format YMD
# [1] = sd_start_date_state - the day when social distancing begins, format YMD H:M:S
# [2] = begin_simul_rl_date - the day RL simulation is begun, format YMD
# [3] = days_of_simul_pre_sd - difference between [0] and [1] 
# [4] = days_of_simul_post_sd - difference between [1] and [2]
# [5] = dry_run_end_diag - number of diagnoses at end of dry run
# [6] = symp_hospitalization_v - the hospitalization data 
# [7] = percent_dead_recover_days_v - recovery and death data
# [8] = pop_dist_v - inital population distribution of susceptible by age and risk group
# [9] = input_list_const_v - list of input parameters
# [10] = q_mat_blank_v - an np array of size 10x10 with values 1 where rates are >0
# [11] = df2 - data frame with the states real time data ####### NAN in the data ############
 

# Function to read and extract indices of the q mat where value is = 1
# Input parameters for this function
# NULL

def reading_indices(Q):
    rate_indices = np.where(Q == 1) 
    list_rate = list(zip(rate_indices[0], rate_indices[1]))
    return list_rate

# Returns 1 value
# A list of length 16, represents the compartment flow; e.g. (0,1) represents 0 -> 1


# Function to extract indices of the diagonal of the q mat where value
# Input parameters for this function
# NULL

def diag_indices_loc(Q):
    mat_size = Q.shape
    diag_index = np.diag_indices(mat_size[0], mat_size[1])
    diag_index_fin = list(zip(diag_index[0], diag_index[1]))
    
    return diag_index_fin

# Returns 1 value
# An np array of size 10x1. Here we have a 10x10 q mat so we have 10 diagonal values. 
# e.g. (0,0) represents 0 -> 0, (1,1) represents 1 -> 1


# Function to read data for all cost, productivity, qalys that calculate the immediate reward
# Input parameters for this function
# NULL

def read_RL_inputs(state, start_rl_sim_date):
    excel = 'data/RL_input.xlsx'
    df = pd.ExcelFile(excel)
    VSL1 = df.parse(sheet_name='VSL_mod') 
    VSL2 = VSL1.to_numpy()
    VSL3 = np.transpose(VSL2)
    VSL = VSL3[:][1]

    lab_for_v = df.parse(sheet_name='labor_for')
    val = lab_for_v[state].values[0] 

    cof_unemploy = df.parse(sheet_name='unemploy_cof_mod', index_col = 0) 
    prop_unemploy = df.parse(sheet_name='unemploy', index_col = 0) 

    K_val = cof_unemploy.loc['K', state]
    A_val = cof_unemploy.loc['A', state]
    h_val = cof_unemploy.loc['h', state]
    x_0 = cof_unemploy.loc['x_0', state]

    datetime_obj = datetime.datetime.strptime(start_rl_sim_date, '%Y%m%d')
    begin_simul_rl_week = datetime_obj.isocalendar()[1]
    if begin_simul_rl_week <= 15:
        init_unemploy = prop_unemploy.loc[begin_simul_rl_week , state]
    else:
        init_unemploy = A_val + (K_val - A_val)/(1 + np.exp(-h_val * (begin_simul_rl_week - x_0)))
        
    return  VSL, val, K_val, A_val, h_val, init_unemploy

# Returns 5 values
# [0] = md_salary - A float scalar of median daily salary lost due to unemployment
# [1] = VSL - A np array of size 101x1 which is the value of statistical life by age 
# [2] = cof_unemploy - A pandas df of 4x49 representing the coefficient of calculation unemployment rate by state
# [3] = prop_unemp - A pandas df of 15x52 representing the unemployment rate for week 1-15 of year 2020 by state
# [4] = labor force - A pandas df of size 1x51 which is the labor force in each state 
        #assumed constant ;calculated by labor participation rate x total population
