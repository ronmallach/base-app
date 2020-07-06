import numpy as np
import pandas as pd
import datetime as dt
import time, os, json, copy

from app.COVID19master import global_var as gv
from app.COVID19master import outputs as op


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
