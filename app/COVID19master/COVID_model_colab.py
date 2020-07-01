import numpy as np
import pandas as pd
import time
import datetime as dt
import os
import json
import copy

from app.COVID19master import global_var1 as gv # RON EDIT
from app.COVID19master import outputs1 as op # RON EDIT
from app.COVID19master import read_policy_mod as rp # RON EDIT

# import global_var1 as gv
# import outputs1 as op
# import read_policy_mod as rp


#import pathlib
#from math import isnan
#import read_policy as rp
# import scenario_analysis_plot as sp
# import write_read_me as rm
# import ImageMerge as im
# from progress.bar import IncrementalBar
# import enlighten

class CovidModel():
    def __init__(self, data=None, heroku=False):
        self.beta_max = gv.beta_before_sd  # max transmission rate (normal pre-COVID 19)
        self.beta_min = gv.beta_after_sd   # min transmission rate ()

        self.enter_state = gv.enter_state  # two letter abbreviation of the state you want to model

        self.tot_risk = gv.tot_risk        # total risk group: female, male
        self.tot_age = gv.tot_age          # total age group: 101, by age

        self.inv_dt = gv.inv_dt    # n time steps in one day
        self.dt = 1/self.inv_dt    # inverse of n time step

        ### simulation related variables; won't change during the simulation
        self.Q = gv.Q                                                      # a base Q-matrix
        self.num_state = self.Q.shape[0]                                   # number of states during the simulation
        self.rates_indices = gv.rates_indices                              # rate matrix for calculating transition rate
        self.diag_indices = gv.diag_indices                                # diagonal matrix for calculating transition rate
        self.symp_hospitalization = gv.symp_hospitalization_v
        self.percent_dead_recover_days = gv.percent_dead_recover_days_v
        self.init_pop_dist = gv.pop_dist_v                                 # initial population distribution
        self.tot_pop = np.sum(self.init_pop_dist)                          # total number of population by State


        self.input_list_const = gv.input_list_const_v                      # input parameters for reading the below parameters
        self.l_days =  self.input_list_const.loc['Days_L', 'value']        # latent period duration
        self.prop_asymp = self.input_list_const.loc['Prop_Asymp', 'value'] # proportion of cases that never show symptoms
        self.incub_days = self.input_list_const.loc['Days_Incub', 'value'] # incubation period duration
        self.a_b = self.input_list_const.loc['a_b', 'value']               # symptom based testing rate
        self.ir_days = self.input_list_const.loc['Days_IR', 'value']       # time from onset of symptoms to recovery
        self.qih_days = self.input_list_const.loc['Days_QiH', 'value']     # time from onset of symptoms to hospitalization
        self.qir_days = self.input_list_const.loc['Days_QiR', 'value']     # time from diagnosis to recovery
        self.second_attack_rate = self.input_list_const.loc['Second_attack', 'value']/100   # second attack rate
        self.hosp_scale = gv.hosp_scale                                    # hospitalization scale factor
        self.dead_scale = gv.dead_scale                                    # death scale factor


        # rl related parameters; won't change during the simulation
        self.lab_for = gv.lab_for                                 # labor force participation rate
        self.VSL = gv.VSL                                         # value of statistical life by age (1-101)
        self.md_salary = gv.md_salary                             # median salary per time step
        self.K_val = gv.K_val                                     # coefficient for calculating unemployment rate
        self.A_val = gv.A_val                                     # coefficient for calculating unemployment rate
        self.duration_unemployment = gv.duration_unemployment     # duration from social distaning to reaching maximum of unemployment rate
        self.cost_tst = gv.test_cost                              # cost of testing per person ([0]: symptom-based,

                                                                  # [1]: contact tracing, [2]: universal testing)
        # read preliminary results
        if data == None:
            self.pre_results = gv.pre_results_dict
        else:
            self.pre_results = data
            if type(self.pre_results['self.next_start_day']) == str:
                self.pre_results['self.next_start_day'] = dt.date(dt.datetime.strptime(self.pre_results['self.next_start_day'], '%m/%d/%Y').year,
                                                                  dt.datetime.strptime(self.pre_results['self.next_start_day'], '%m/%d/%Y').month,
                                                                  dt.datetime.strptime(self.pre_results['self.next_start_day'], '%m/%d/%Y').day)
            self.pre_results['self.pop_dist_sim'] = np.array(self.pre_results['self.pop_dist_sim'])
            self.pre_results['self.num_diag'] = np.array(self.pre_results['self.num_diag'])
            self.pre_results['self.num_dead'] = np.array(self.pre_results['self.num_dead'])
            self.pre_results['self.num_hosp'] = np.array(self.pre_results['self.num_hosp'])
            self.pre_results['self.num_trac_test'] = np.array(self.pre_results['self.num_trac_test'])
            self.pre_results['self.num_uni_test'] = np.array(self.pre_results['self.num_uni_test'])
            self.pre_results['self.num_base_test'] = np.array(self.pre_results['self.num_base_test'])
            
            
            
        # start making decisions from today
        self.decision_making_day = pd.Timestamp.today().date()

        # the end of day from preliminatry simulation
        self.sim_start_day = self.pre_results['self.next_start_day']

        # number of days before decision making
        if self.decision_making_day >= self.sim_start_day:

            self.pre_sim_days = abs(self.decision_making_day - self.sim_start_day).days
        else:
            self.pre_sim_days = 0

        # total simulation time period
        self.T_total = self.inv_dt * (gv.T_max + self.pre_sim_days)

        # initialize observation
        self.op_ob = op.output_var(sizeofrun =int(self.T_total/self.inv_dt), state = self.enter_state,
                                   start_d = self.sim_start_day, decision_d = self.decision_making_day)
        # initialize simulation
        self.init_sim()

    # Function to simulate compartment transition, calculate immediate reward function and output result
    # Input parameter:
    # action_t = a NumPy array of size [1x3] with the values output by the RL model (a_sd, T_c, T_u)
    def step(self, action_t):
        self.policy[self.t] = action_t
        self.set_action(action_t) # run it when action is a_sd, T_c, T_u
        # self.set_action_mod(action_t)  # run it when action is a_sd, a_c, a_u
        self.simulation_base()
        self.calc_imm_reward()
        self.output_result()

    # Function to output result for plotting
    # Input parameters:
    # NULL
    def output_result(self):
        if self.t % self.inv_dt == 0:

            self.op_ob.time_step[self.d] = self.d     # timestep (day)
            #### if plot for the day
            indx_l = self.t - self.inv_dt + 1 # = self.t
            indx_u = self.t + 1  # = self.t + 1

            self.op_ob.num_inf_plot[self.d] = np.sum(self.num_diag[indx_l: indx_u])          # new infected for the day
            self.op_ob.num_hosp_plot[self.d] = np.sum(self.num_hosp[indx_l: indx_u])         # new hospitablization for the day
            self.op_ob.num_dead_plot[self.d] = np.sum(self.num_dead[indx_l: indx_u])         # new death for the day
            self.op_ob.cumulative_inf[self.d] =  self.tot_num_diag[self.t]                   # cumulative infections from start of simulation to the day
            self.op_ob.cumulative_hosp[self.d] = self.tot_num_hosp[self.t]                   # cumulative hospitalizations from start of simulation to the day
            self.op_ob.cumulative_dead[self.d] = self.tot_num_dead[self.t]                   # cumulative dead from start of simulation to the day

            self.op_ob.num_base[self.d] = np.sum(self.num_base_test[indx_l: indx_u])         # number of symptom based testing for the day
            self.op_ob.num_uni[self.d] = np.sum(self.num_uni_test[indx_l: indx_u])           # number of universal testing for the day
            self.op_ob.num_trac[self.d] = np.sum(self.num_trac_test[indx_l: indx_u])         # number of contact tracing based testing for the day

            self.op_ob.VSL_plot[self.d] =  (np.sum(self.Final_VSL[indx_l: indx_u]))          # VSL at timestep t
            self.op_ob.SAL_plot[self.d] =  (np.sum(self.Final_SAL[indx_l: indx_u]))          # SAL at timestep t
            self.op_ob.unemployment[self.d] = self.rate_unemploy[self.t]                     # unemployment rate at time step t
            self.op_ob.univ_test_cost[self.d] =  (np.sum(self.cost_test_u[indx_l: indx_u]))  # cost of universal testing for the day
            self.op_ob.trac_test_cost[self.d] =  (np.sum(self.cost_test_c[indx_l: indx_u]))  # cost of contact tracing for the day
            self.op_ob.bse_test_cost[self.d] =  (np.sum(self.cost_test_b[indx_l: indx_u]))   # symptom based testing for the day

            self.op_ob.num_diag_inf[self.d] = self.num_diag_inf[self.t]                      # Q_L + Q_E + Q_I
            self.op_ob.num_undiag_inf[self.d] = self.num_undiag_inf[self.t]                  # L + E + I
            self.op_ob.policy_plot[self.d] = self.policy[self.t]                             # policy

            # plot for analysis
            self.op_ob.T_c_plot[self.d] = self.T_c                                           # Plot number of contact tracing
            self.op_ob.tot_test_cost_plot[self.d] = self.op_ob.univ_test_cost[self.d] + \
                                                    self.op_ob.trac_test_cost[self.d] + \
                                                    self.op_ob.bse_test_cost[self.d]

            self.d += 1 # update day

            # gv.prog_bar.next()

    # Function to convert action
    # Input parameter:
    # action_t = a NumPy array of size [1x3] with the values output by the RL model (a_sd, a_c, a_u)
    def set_action_mod(self, action_t):
        self.a_sd = action_t[0]
        self.a_c = action_t[1]
        self.a_u = action_t[2]
        self.T_u = self.a_u * np.sum(self.pop_dist_sim[(self.t - 1),:,:,0:4])
        self.T_c = self.a_c * ((1 - self.a_u) * np.sum(self.pop_dist_sim[(self.t - 1),:,:,1:4])) / self.second_attack_rate


    # Function to convert action
    # Input parameter:
    # action_t = a NumPy array of size [1x3] with the values output by the RL model (a_sd, T_c, T_u)
    def set_action(self, action_t):
        self.a_sd = action_t[0]
        self.T_c = action_t[1]
        self.T_u = action_t[2]
        self.a_u = self.T_u / np.sum(self.pop_dist_sim[(self.t - 1),:,:,0:4])
        self.a_c = min(1, (self.T_c * self.second_attack_rate)/((1 - self.a_u) * np.sum(self.pop_dist_sim[(self.t - 1),:,:,1:4])))

    # Function to calculate immediate reward /cost
    # Input parameter:
    # NULL
    def calc_imm_reward(self):
        million = 1000000 # one million dollars

        self.calc_unemployment()

        tot_alive = self.tot_pop - self.tot_num_dead[self.t - 1]   # total number of alive people at time step (t - 1)

        # number of unemployed = total alive people at time step (t - 1) x labor force participation rate /100
        #                        x unemployment rate
        num_unemploy = tot_alive * self.rate_unemploy[self.t - 1] * self.lab_for  # rate converted to percentage

        # calculate total wage loss due to contact reducation  = number of unemployed x median wage / 1 million
        self.Final_SAL[self.t] = num_unemploy * self.md_salary * self.dt / million

        # calculate total 'value of statistical life' loss due to deaths = number of newly dead x VSL (by age)
        num_dead = np.sum(self.num_dead[self.t - 1], axis = 0)
        self.Final_VSL[self.t]  = np.sum(np.dot(num_dead , self.VSL))

        # calculate cost of testing
        self.cost_test_b[self.t] =  self.cost_tst[0] * np.sum(self.num_base_test[self.t]) /million
        self.cost_test_c[self.t] =  self.dt * self.cost_tst[1] * self.a_c * (1 - self.a_u) * np.sum(self.pop_dist_sim[(self.t - 1),:,:,1:4]) /(self.second_attack_rate * million)
        self.cost_test_u[self.t] =  self.dt * self.cost_tst[2] * self.T_u / million
        self.Final_TST[self.t] = self.cost_test_u[self.t] + self.cost_test_c[self.t] + self.cost_test_b[self.t]

        # calculate immeidate reward
        self.imm_reward[self.t] = -1 * (self.Final_VSL[self.t]  + self.Final_SAL[self.t] + self.Final_TST[self.t])

    # Function to calculate unemployment change
    # Input parameter:
    # NULL
    def calc_unemployment(self):
        y_p = self.rate_unemploy[self.t-1]

        K = max(self.a_sd * self.K_val, y_p)

        A = max(self.A_val, min(self.a_sd * self.K_val, y_p))

        u_plus = (K - A)/self.duration_unemployment

        u_minus = 0.5 * (K - A)/self.duration_unemployment
        if y_p == K:
            self.rate_unemploy[self.t] = y_p - u_minus * self.dt
        else:
            self.rate_unemploy[self.t] = y_p + u_plus *  self.dt

    # Function to calculate transition rates (only for the rates that won't change by risk or age)
    # Input parameter:
    # NULL
    def set_rate_array(self):
        # rate of S -> L
        beta_sd = self.beta_min + (1 - self.a_sd) * (self.beta_max - self.beta_min) ### modify this equation to take beta value
        self.rate_array[0] = (beta_sd * np.sum(self.pop_dist_sim[(self.t - 1),\
                              :,:,2:4]))/(np.sum(self.pop_dist_sim[(self.t - 1), :,:,0:9]))
        # rate of L -> E
        self.rate_array[1] = 1/self.l_days
        # rate of L -> Q_L
        self.rate_array[2] = self.a_u + ((1 - self.a_u)*self.a_c)
        # rate of E -> Q_E
        self.rate_array[4] = self.a_u + ((1 - self.a_u)*self.a_c)
        # rate of E -> Q_I
        self.rate_array[6] = self.prop_asymp/(self.incub_days - self.l_days)
        # rate of I -> Q_I
        self.rate_array[7] = self.a_b
        # rate of I -> R
        self.rate_array[8] = ((self.a_u + (1-self.a_u)*self.a_c)) + 1/self.ir_days
        # rate of Q_L -> Q_E
        self.rate_array[9] = 1/self.l_days


    # Function to perform the simulation
    # Input parameters
    # NULL

    # 0	1	2	3	4	5	6	7	8	9 compartments
    # S	L	E	I	Q_L	Q_E	Q_I	H	R	D compartments
    def simulation_base(self):
        # Calculate transition rate that won't change during the for loop
        self.set_rate_array()

        for risk in range(self.tot_risk): # for each risk group i.e, male(0) and female(1)

            for age in range (self.tot_age): # for each age group i.e., from 0-100

                for i1 in range(self.symp_hospitalization.shape[0]):

                    if((age >= self.symp_hospitalization[i1, 0])&(age <= self.symp_hospitalization[i1, 1])):

                        # rate of E -> I
                        self.rate_array[3] = (1 - self.symp_hospitalization[i1,2] * (1 - self.prop_asymp))/(self.incub_days - self.l_days)
                        # rate of E -> Q_I
                        self.rate_array[5] = (self.symp_hospitalization[i1,2]*(1 - self.prop_asymp))/(self.incub_days - self.l_days)
                        # rate of Q_E -> Q_I
                        self.rate_array[10] = (self.a_b * (1 - self.symp_hospitalization[i1,2]) + self.symp_hospitalization[i1,2]) * (1 - self.prop_asymp)/(self.incub_days - self.l_days)
                        # rate of Q_E -> R
                        self.rate_array[11] = (1 - (self.a_b * (1 - self.symp_hospitalization[i1,2]) + self.symp_hospitalization[i1,2]) *  (1 - self.prop_asymp))/(self.incub_days - self.l_days)
                        # rate of Q_I to H
                        self.rate_array[12] = (self.hosp_scale * self.symp_hospitalization[i1,2])/self.qih_days
                        # rate of Q_I to R
                        self.rate_array[13]= (1 - self.hosp_scale * self.symp_hospitalization[i1,2])/self.qir_days


                for i2 in range(self.percent_dead_recover_days.shape[0]):
                    if((age >= self.percent_dead_recover_days[i2,0])&(age <= self.percent_dead_recover_days[i2,1])):
                        # rate of H to D
                        self.rate_array[14] = (1 - (self.dead_scale * self.percent_dead_recover_days[i2,risk + 2]/100))/(self.percent_dead_recover_days[i2, 5])
                        # rate of H to R
                        self.rate_array[15] = (self.dead_scale * self.percent_dead_recover_days[i2,risk + 2]/100)/(self.percent_dead_recover_days[i2, 4])


                # Initialize a new Q-matrix that will change over the simulation
                Q_new = np.zeros((self.num_state, self.num_state))

                for i3 in range(len(self.rates_indices)):
                    Q_new[self.rates_indices[i3]] = self.rate_array[i3]

                row_sum = np.sum(Q_new, 1)

                for i4 in range(len(row_sum)):
                    Q_new[self.diag_indices[i4]] = row_sum[i4]*(-1)

                pop_dis_b = self.pop_dist_sim[self.t - 1][risk][age].reshape((1, self.num_state))
                # population distribution state transition
                self.pop_dist_sim[self.t][risk][age] = pop_dis_b + np.dot(pop_dis_b, (Q_new * self.dt))
                # number of new hospitalized at time step t
                self.num_hosp[self.t][risk][age] = pop_dis_b[0,6] * self.dt *  self.rate_array[12]
                # number of new death at time step t
                self.num_dead[self.t][risk][age] = pop_dis_b[0,7] * self.dt *  self.rate_array[15]
                # number of diagnosis through symptom based testing
                self.num_base_test[self.t][risk][age] = pop_dis_b[0,3] * self.dt * self.rate_array[7] + pop_dis_b[0,2] * self.dt * self.rate_array[5]
                # number of diagnosis through universal testing
                self.num_uni_test[self.t][risk][age] = (pop_dis_b[0,1] + pop_dis_b[0,2] + pop_dis_b[0,3]) * self.dt * self.a_u
                # number of diagnosis through contact tracing
                self.num_trac_test[self.t][risk][age] = (pop_dis_b[0,1] + pop_dis_b[0,2] + pop_dis_b[0,3]) * self.dt * (1 - self.a_u) * self.a_c

        # the total number of diagnosis
        self.num_diag[self.t] = self.num_base_test[self.t] + self.num_trac_test[self.t] + self.num_uni_test[self.t]

        # update total number of diagnosis, hospitalizations and deaths
        self.tot_num_diag[self.t] = self.tot_num_diag[self.t - 1] + np.sum(self.num_diag[self.t])
        self.tot_num_hosp[self.t] = self.tot_num_hosp[self.t - 1] + np.sum(self.num_hosp[self.t])
        self.tot_num_dead[self.t] = self.tot_num_dead[self.t - 1] +np.sum(self.num_dead[self.t])

        self.num_diag_inf[self.t] = np.sum(self.pop_dist_sim[self.t,:,:,4:7])
        self.num_undiag_inf[self.t] = np.sum(self.pop_dist_sim[self.t,:,:,1:4])

    # Function to run simulate results until start of decision making
    # Input parameter:
    # NULL
    def pre_decision_sim(self):
        # print('pre_decision_sim begins')

        while self.t <=  self.pre_sim_days * self.inv_dt:
            self.t += 1
            self.step(action_t = np.array([1, 0, 0]))

        # print('pre_decision_sim ends')

    # Function to intialize simulation
    # Input parameter:
    # NULL
    def init_sim(self):
        # print("reset_sim begin")
        self.d = 0
        self.t = 0
        self.rate_array = np.zeros([16 ,1])     # initialize rate array

        # Initialize measures for epidemics
        self.num_diag = np.zeros((self.T_total + 1, self.tot_risk, self.tot_age))        # number of diagnosis
        self.num_dead = np.zeros((self.T_total + 1, self.tot_risk, self.tot_age))        # number of deaths
        self.num_hosp = np.zeros((self.T_total + 1, self.tot_risk, self.tot_age))        # number of hospitalizations

        self.pop_dist_sim = np.zeros((self.T_total + 1, self.tot_risk, \
                                      self.tot_age, self.num_state))                     # population distribution by risk, age and epidemic state

        self.num_base_test = np.zeros((self.T_total + 1, self.tot_risk, self.tot_age))   # number of diagnosed through symptom-based testing
        self.num_uni_test = np.zeros((self.T_total + 1, self.tot_risk, self.tot_age))    # number of diagnosed through universal testing
        self.num_trac_test = np.zeros((self.T_total + 1, self.tot_risk, self.tot_age))   # number of diagnosed through contact tracing

        self.tot_num_diag = np.zeros(self.T_total + 1)                                   # cumulative diagnosed
        self.tot_num_dead = np.zeros(self.T_total + 1)                                   # cumulative deaths
        self.tot_num_hosp = np.zeros(self.T_total + 1)                                   # cumulative hospitalizations

        self.num_diag_inf = np.zeros(self.T_total + 1)                                   # Q_L + Q_E + Q_I
        self.num_undiag_inf = np.zeros(self.T_total + 1)                                 # L + E + I

        # initialize action
        self.a_sd = 0
        self.a_c = 0
        self.a_u = 0
        self.T_c = 0
        self.T_u = 0

        # Initialize immediate reward related parameters
        self.imm_reward = np.zeros(self.T_total + 1)
        self.Final_VSL = np.zeros(self.T_total + 1)
        self.Final_SAL = np.zeros(self.T_total + 1)
        self.Final_TST = np.zeros(self.T_total + 1)
        self.cost_test_u = np.zeros(self.T_total + 1)
        self.cost_test_c = np.zeros(self.T_total + 1)
        self.cost_test_b = np.zeros(self.T_total + 1)
        self.rate_unemploy = np.zeros(self.T_total + 1)
        self.policy = np.zeros((self.T_total + 1, 3))

        # Initialize parameters of t = 0 as the day before the start day of the simulation
        self.pop_dist_sim[0] = self.pre_results['self.pop_dist_sim'].reshape(self.pop_dist_sim[0].shape)
        self.num_diag[0] = self.pre_results['self.num_diag'].reshape(self.num_diag[0].shape)
        self.num_hosp[0] = self.pre_results['self.num_hosp'].reshape(self.num_hosp[0].shape)
        self.num_dead[0] = self.pre_results['self.num_dead'].reshape(self.num_dead[0].shape)

        self.num_base_test[0] = self.pre_results[ 'self.num_base_test'].reshape(self.num_base_test[0].shape)
        self.num_uni_test[0] = self.pre_results['self.num_uni_test'].reshape(self.num_uni_test[0].shape)
        self.num_trac_test[0] = self.pre_results['self.num_trac_test'].reshape(self.num_trac_test[0].shape)
        self.tot_num_diag[0] = self.pre_results['self.tot_num_diag']
        self.tot_num_dead[0] = self.pre_results['self.tot_num_dead']
        self.tot_num_hosp[0] = self.pre_results['self.tot_num_hosp']
        self.rate_unemploy[0] = self.pre_results['self.rate_unemploy']

        # run simulation before decision making
        self.pre_decision_sim()
        # print('init stemim ends')



decision = np.array([[1.1818e+02, 1.1818e+02, 9.3000e-01],
       [1.1818e+02, 1.1818e+02, 9.3000e-01],
       [1.1818e+02, 1.1818e+02, 9.3000e-01],
       [1.1818e+02, 1.1818e+02, 9.3000e-01],
       [1.1818e+02, 1.1818e+02, 9.3000e-01],
       [1.1818e+02, 1.1818e+02, 9.3000e-01],
       [1.1818e+02, 1.1818e+02, 9.3000e-01],
       [1.1818e+02, 1.1818e+02, 9.3000e-01],
       [1.1818e+02, 1.1818e+02, 9.3000e-01],
       [1.3636e+02, 1.3636e+02, 8.6000e-01],
       [1.3636e+02, 1.3636e+02, 8.6000e-01],
       [1.3636e+02, 1.3636e+02, 8.6000e-01],
       [1.3636e+02, 1.3636e+02, 8.6000e-01],
       [1.3636e+02, 1.3636e+02, 8.6000e-01],
       [1.3636e+02, 1.3636e+02, 8.6000e-01],
       [1.3636e+02, 1.3636e+02, 8.6000e-01],
       [1.5455e+02, 1.5455e+02, 8.0000e-01],
       [1.5455e+02, 1.5455e+02, 8.0000e-01],
       [1.5455e+02, 1.5455e+02, 8.0000e-01],
       [1.5455e+02, 1.5455e+02, 8.0000e-01],
       [1.5455e+02, 1.5455e+02, 8.0000e-01],
       [1.5455e+02, 1.5455e+02, 8.0000e-01],
       [1.5455e+02, 1.5455e+02, 8.0000e-01],
       [1.7273e+02, 1.7273e+02, 7.3000e-01],
       [1.7273e+02, 1.7273e+02, 7.3000e-01],
       [1.7273e+02, 1.7273e+02, 7.3000e-01],
       [1.7273e+02, 1.7273e+02, 7.3000e-01],
       [1.7273e+02, 1.7273e+02, 7.3000e-01],
       [1.7273e+02, 1.7273e+02, 7.3000e-01],
       [1.7273e+02, 1.7273e+02, 7.3000e-01],
       [1.9091e+02, 1.9091e+02, 6.6000e-01],
       [1.9091e+02, 1.9091e+02, 6.6000e-01],
       [1.9091e+02, 1.9091e+02, 6.6000e-01],
       [1.9091e+02, 1.9091e+02, 6.6000e-01],
       [1.9091e+02, 1.9091e+02, 6.6000e-01],
       [1.9091e+02, 1.9091e+02, 6.6000e-01],
       [1.9091e+02, 1.9091e+02, 6.6000e-01],
       [2.0909e+02, 2.0909e+02, 5.9000e-01],
       [2.0909e+02, 2.0909e+02, 5.9000e-01],
       [2.0909e+02, 2.0909e+02, 5.9000e-01],
       [2.0909e+02, 2.0909e+02, 5.9000e-01],
       [2.0909e+02, 2.0909e+02, 5.9000e-01],
       [2.0909e+02, 2.0909e+02, 5.9000e-01],
       [2.0909e+02, 2.0909e+02, 5.9000e-01],
       [2.2727e+02, 2.2727e+02, 5.2000e-01],
       [2.2727e+02, 2.2727e+02, 5.2000e-01],
       [2.2727e+02, 2.2727e+02, 5.2000e-01],
       [2.2727e+02, 2.2727e+02, 5.2000e-01],
       [2.2727e+02, 2.2727e+02, 5.2000e-01],
       [2.2727e+02, 2.2727e+02, 5.2000e-01],
       [2.2727e+02, 2.2727e+02, 5.2000e-01],
       [2.4545e+02, 2.4545e+02, 4.5000e-01],
       [2.4545e+02, 2.4545e+02, 4.5000e-01],
       [2.4545e+02, 2.4545e+02, 4.5000e-01],
       [2.4545e+02, 2.4545e+02, 4.5000e-01],
       [2.4545e+02, 2.4545e+02, 4.5000e-01],
       [2.4545e+02, 2.4545e+02, 4.5000e-01],
       [2.4545e+02, 2.4545e+02, 4.5000e-01],
       [2.6364e+02, 2.6364e+02, 3.9000e-01],
       [2.6364e+02, 2.6364e+02, 3.9000e-01],
       [2.6364e+02, 2.6364e+02, 3.9000e-01],
       [2.6364e+02, 2.6364e+02, 3.9000e-01],
       [2.6364e+02, 2.6364e+02, 3.9000e-01],
       [2.6364e+02, 2.6364e+02, 3.9000e-01],
       [2.6364e+02, 2.6364e+02, 3.9000e-01],
       [2.8182e+02, 2.8182e+02, 3.2000e-01],
       [2.8182e+02, 2.8182e+02, 3.2000e-01],
       [2.8182e+02, 2.8182e+02, 3.2000e-01],
       [2.8182e+02, 2.8182e+02, 3.2000e-01],
       [2.8182e+02, 2.8182e+02, 3.2000e-01],
       [2.8182e+02, 2.8182e+02, 3.2000e-01],
       [2.8182e+02, 2.8182e+02, 3.2000e-01],
       [3.0000e+02, 3.0000e+02, 2.5000e-01],
       [3.0000e+02, 3.0000e+02, 2.5000e-01],
       [3.0000e+02, 3.0000e+02, 2.5000e-01],
       [3.0000e+02, 3.0000e+02, 2.5000e-01],
       [3.0000e+02, 3.0000e+02, 2.5000e-01],
       [3.0000e+02, 3.0000e+02, 2.5000e-01],
       [3.0000e+02, 3.0000e+02, 2.5000e-01]])

inv_dt = 1

# Funtion for one scenario analysis
def main_run(State='NY', decision=decision, uw=50, costs=[50,50,50],
             T_max=decision.shape[0]-1, data=None, 
             pre_data = None, heroku=False, max_time=25):
    #decision = set_up_COVID_sim(State)
    # mod costs
    path = os.getcwd()
    state = State
    inv_dt = 10               # insert time steps within each day
    gv.setup_global_variables(state, inv_dt, path, heroku=False) 
    gv.md_salary = uw
    gv.test_cost = costs
    gv.T_max = T_max
    #sample_model = run_COVID_sim(decision, static='N', data=data)
    timer, time_start = 0, time.time()
    model = CovidModel(data=data, heroku=heroku)
    i = 0
    d_m = decision[i]
    print(model.T_total)
    while model.t < model.T_total and (timer < max_time or i % model.inv_dt != 0):
        model.t += 1
        if model.t % 25 == 0: print('t', model.t, np.round(timer, 2))
        if i % model.inv_dt == 0:
            d_m = decision[i//model.inv_dt]
        model.step(action_t = d_m)
        i += 1
        timer = time.time() - time_start
    mod = model.t - model.d * model.inv_dt 
    date_range = pd.date_range(start= model.sim_start_day, periods= model.d, freq = 'D')

    # print(type(date_range[-1])
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

    output = model.op_ob.write_output(pre_results = gv.pre_results_df, date_range = date_range, pre_data = pre_data)
    remaining_decision = decision[i//model.inv_dt :]
    is_complete = 'True' if model.T_total - model.t <= 2 else 'False'
    results = {'pre_data':dic, 'to_java':output, 'remaining_decision':remaining_decision,
               'is_complete':is_complete}
    results = prep_results_for_java(results)
    return results


def prep_results_for_java(results):
    results = copy.deepcopy(results)
    results['is_complete'] = str(results['is_complete'])
    if results['to_java'] == None:
        results['to_java'] = json.dumps(results['to_java'])
    else:
        df1, df2, df3, df4, df5 = results['to_java']
        temp = {'VSL':df1,'Unemployment':df2,'Testing':df3,'Summary':df4,'Decision Choice':df5}
        temp['Summary']['Date'] = temp['Summary'].index.astype(str)
        for k,v in temp.items():
            temp[k].index = temp[k].index.astype(str)
        results['to_java'] = {k : json.dumps(v.astype(str).to_dict('index')) for k,v in temp.items()}
    results['remaining_decision'] = json.dumps(results['remaining_decision'].tolist())
    results['pre_data'] = json.dumps(results['pre_data'])
    return results

def prep_input_for_python(results):
    results = copy.deepcopy(results)
    for plan, instructions in results.items():
        if plan in ['A', 'B', 'C']:
            print(instructions['to_java'])
            if instructions['to_java'] != 'null':
                instructions['to_java'] = [pd.read_json(v).T for v in instructions['to_java'].values()]
            else:
                instructions['to_java'] = None
            instructions['remaining_decision'] = np.array(json.loads(instructions['remaining_decision']))
            instructions['pre_data'] = json.loads(instructions['pre_data'])
            results[plan] = instructions
    return results

#         for k,v in output.items():
#             output[k].index = output[k].index.astype(str)
#         results[plan] = {k : json.dumps(v.astype(str).to_dict('index')) for k,v in output.items()}


# # Function to run COVID model simulation
# # static - static decision choice
# def run_COVID_sim(decision, static = 'N', data=None):
#     # mod costs
#     timer, max_time, time_start = 0, 25, time.time()
#     sample_model = CovidModel(data=data)
#     if static == 'N' :
#         i = 0
#         d_m = decision[i]
#         while sample_model.t < sample_model.T_total  and timer < max_time:
#             # print("##### step begin #####")
#             # print('The code is running')
#             sample_model.t += 1
#             # print('t', sample_model.t)
#             if i % sample_model.inv_dt == 0:
#                 d_m = decision[i//sample_model.inv_dt]
#             sample_model.step(action_t = d_m)
#             i += 1
#             timer = time.time() - time_start
#             # print("##### step end ##### \n")
#     # else:
#     #     while sample_model.t < sample_model.T_total:
#     #         sample_model.t += 1
#     #         sample_model.step(action_t = decision)
#     return sample_model


# # Function to set up COVID model (only need to initialize once)
# def set_up_COVID_sim(State):
#     state = State
#     inv_dt = 10             # insert time steps within each day
#     gv.setup_global_variables(state, inv_dt)
#     cost_path = pathlib.Path('data/cost.xlsx')
#     # set value for user defined inputs
#     gv.md_salary, gv.test_cost =  gv.read_cost(cost_path)
#     # policy_path = pathlib.Path('data/policy_example.xlsx') # for main use
#     policy_path = pathlib.Path('data/policy_test.xlsx')  # for test purpose only (original assumption)
#     decision = rp.read_policy(policy_path)
#     gv.T_max = decision.shape[0]
#     # gv.prog_bar = IncrementalBar('Code In Processing: \t', max =  gv.T_max)
#     print('\n')
#     return decision


# # Function for scenario comparison analysis - Colab
# def compare_scenarios_colab(State, A_l):
#     # eg.Str_l = ['1,0.2,10,0.4','20,0.6','17,0.8,300,0.9']
#     # Str_L = [Str_l,Str_l,Str_l]
#     # A_L = [Str_L,Str_L]
#     # set_up_COVID_sim(State)
#     tables = len(A_l)
#     N = 0
#     for i in range(tables):
#         N += len(A_l[i])
#     run = 0
#     for table in range(tables):
#         # table_path = pathlib.Path('results/table%d.xlsx'%(table+1))
#         table_path = pathlib.Path('results/results.xlsx')
#         writer = pd.ExcelWriter(table_path, engine = 'xlsxwriter')
#         # names = []
#         policy_index = []

#         for i in range(len(A_l[table])):
#             Str_l  = A_l[table][i]
#             ts = time.time()
#             run +=1
#             print('doing run %d'%run)

#             decision = rp.get_policy(Str_l)
#             gv.T_max =decision.shape[0]
#             model = run_COVID_sim(decision, static = 'N')
#             df, start_d, decision_d  = model.op_ob.write_scenario_needed_results_colab(gv.pre_results_df)

#             # name = 'a_sd' + Str_l[0] +'\n'
#             # name += 'a_c' + Str_l[1] +'\n'
#             # name += 'a_u' + Str_l[2]

#             # names.append(name)
#             policy_index.append('scenario' + str(i+1))
#             df.to_excel(writer, sheet_name = 'scenario' + str(i+1))

#             tu = time.time() - ts
#             print('run %d finished time used : %f sec'%(run,tu) )
#             print('expected time left: %f min'%(tu*(N - run)/60))

#         pd.DataFrame(policy_index).to_excel(writer, sheet_name = 'interventions')

#         readme = rm.write_rm()
#         readme.to_excel(writer, sheet_name = 'README')
#         writer.save()
#     # return table, start_d, decision_d
#     return table_path, start_d, decision_d


# Function for scenario comparison analysis - Excel sheet
# def compare_scenarios(State, A_l):
#     set_up_COVID_sim(State)
#     tables = A_l.shape[1]//3
#     N =(A_l.shape[0] * A_l.shape[1] - np.sum(A_l.isna().values))//3 # total number of scenarios
#     run = 0

#     for table in range(tables):
#         table_path = pathlib.Path('results/table%d.xlsx'%(table+1))
#         writer = pd.ExcelWriter(table_path, engine = 'xlsxwriter')
#         names = []

#         for i in range(A_l.shape[0]):
#             if not isnan(A_l.values[i,3*table]):
#                 ts = time.time()
#                 run +=1
#                 print('Runing Scenario %d'%run)

#                 a_c = A_l.values[i,3 * table]
#                 a_sd = A_l.values[i,3 * table + 1]
#                 a_u =  A_l.values[i,3 * table + 2]
#                 decision = [float(a_sd),float(a_c),float(a_u)]
#                 model = run_COVID_sim(decision, static = 'Y')
#                 df = model.op_ob.write_scenario_needed_results(gv.pre_results_df)
#                 name = 'a_sd = %.f%%, a_c = %.f%%, a_u = %.f%%'%(100*a_sd,100*a_c, 100*a_u)
#                 names.append(name)
#                 df.to_excel(writer, sheet_name = name)

#                 tu = time.time() - ts
#                 print('Time spent on running Scenario %d: %f sec'%(run,tu) )
#                 print('Expected time left: %f min'%(tu * (N - run)/60))

#             else:
#                 break
#         pd.DataFrame(names).to_excel(writer, sheet_name = 'interventions')
#         writer.save()

#     return tables


# # Function to return action list
# def return_A_list(i):

#         print('This is Scenario ' + str(i + 1))

#         #### The daily scenario is being used so the text here should be modified, yet to modified.
#         # a_sd_str, a_c_str, a_u_str
#         # '1,0.2,10,0.4' means day 1 to day 1 use 0.2; day 2 to day 10 use 0.4

#         a_sd_str = input('Enter value here: ')

#         a_c_str = input('Enter value here: ')

#         a_u_str = input('Enter value here: ')

#         return [a_sd_str, a_c_str, a_u_str]
#         # return value is in the form of  ['1,0.2,10,0.4','20,0.6','17,0.8,300,0.9']

# # Function to modify intervention related to costs
# def mod_cost():
#     bol_c = 'N'  # default value
#     bol_c =input('Enter Y or N: ')
#     if bol_c == 'Y' or bol_c == 'y':
#         gv.md_salary = float(input('Enter median daily wage here: '))
#         gv.test_cost[0] = float(input('Enter unit cost of symptom-based testing here: '))
#         gv.test_cost[1] = float(input('Enter unit cost of contact tracing testing here: '))
#         gv.test_cost[2] = float(input('Enter unit cost of universal testing here: '))
#         gv.md_salary = gv.md_salary /8 *(40/7)   # to convert median daily wage


# # Function to modify decisions
# def mod_decisions_run():

#     bol_ = 'Y' # default change decisions
#     print('\n')
#     if bol_ == 'Y' or bol_ =='y':
#         # N_scenario is the number of scenarios/policies you wanna run
#         N_scenario = input('Enter value here: ')
#         Str_L = []
#         for i in range(int(N_scenario)):
#             Str_L.append(return_A_list(i))

#         mod_cost()
#         table_path, start_d, decision_d = compare_scenarios_colab(State, A_l = [Str_L]) # run simulation
#         sp.plot_results_colab(table_path, start_d, decision_d, gv.pre_results_df) # plot results
#         # im.merge_image_colab()     # merge images

#     else:
#         main_run(State)

# if  __name__ == "__main__":

#     State = 'NY' # default is New York
#     set_up_COVID_sim(State)   # initialize model
#     mod_decisions_run()       # modify decision choice and simulate
