#### if action  = [a_sd, a_c, a_u] -> uncomment self.set_action_mod() in self.step()
#### else action  = [a_sd, T_c, T_u] -> uncomment self.set_action() in self.step()
import numpy as np 
import pandas as pd
from datetime import datetime

import global_var_pre_dm as gv
import outputs_pre_dm as op

class CovidModel():
    def __init__(self):

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
        self.dry_run_end_diag = gv.dry_run_end_diag                        # after dry run, total number of diagnosis should match with data
        self.days_of_simul_pre_sd = gv.days_of_simul_pre_sd                # number of days before social distancing
        self.days_of_simul_post_sd = gv.days_of_simul_post_sd              # number of days after social distancing before the end of observed data

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

        # simulation time period since dry run
        self.T_total = self.inv_dt * (self.days_of_simul_pre_sd + self.days_of_simul_post_sd) # simulation time period from dry run
      
        # rl related parameters; won't change during the simulation 
        self.lab_for = gv.lab_for                                 # labor force participation rate 
        self.VSL = gv.VSL                                         # value of statistical life by age (1-101)
        self.md_salary = gv.md_salary                             # median salary per time step 
        self.K_val = gv.K_val                                     # coefficient for calculating unemployment rate
        self.A_val = gv.A_val                                     # coefficient for calculating unemployment rate
        self.duration_unemployment = gv.duration_unemployment     # duration from social distaning to reaching maximum of unemployment rate
        self.cost_tst = gv.test_cost                              # cost of testing per person ([0]: symptom-based, 
                                                                  # [1]: contact tracing, [2]: universal testing)
        # initialize observation 
        self.op_ob = op.output_var(int(self.T_total/self.inv_dt) + 1, state = self.enter_state)

        # initialize simulation                        
        self.init_sim()                                          # initialize the simulation 
    
    # Function to simulate compartment transition, calculate immediate reward function and output result
    # Input parameter:
    # action_t = a NumPy array of size [1x3] with the values output by the RL model (a_sd, T_c, T_u)
    def step(self, action_t):
        self.policy[self.t] = action_t
        # self.set_action(action_t) # run it when action is a_sd, T_c, T_u
        self.set_action_mod(action_t)  # run it when action is a_sd, a_c, a_u
        self.simulation_base() 
        self.calc_imm_reward()
        self.output_result() 

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

    # Function to output result for plotting
    # Input parameters: 
    # NULL
    def output_result(self):
        if self.t % self.inv_dt == 0:             
            self.op_ob.time_step[self.d] = self.d     # timestep (day)
            #### if plot for the day 
            indx_l = self.t - self.inv_dt + 1 # = self.t
            indx_u = self.t + 1  # = self.t + 1

            self.op_ob.num_inf_plot[self.d] = np.sum(self.num_diag[indx_l: indx_u])          # new diagnosis for the day
            self.op_ob.num_hosp_plot[self.d] = np.sum(self.num_hosp[indx_l: indx_u])         # new hospitablization for the day
            self.op_ob.num_dead_plot[self.d] = np.sum(self.num_dead[indx_l: indx_u])         # new death for the day
            self.op_ob.num_new_inf_plot[self.d] = np.sum(self.num_new_inf[indx_l: indx_u])   # new infection for the day
            self.op_ob.cumulative_inf[self.d] =  self.tot_num_diag[self.t]                   # cumulative infections from start of simulation to the day
            self.op_ob.cumulative_hosp[self.d] = self.tot_num_hosp[self.t]                   # cumulative hospitalizations from start of simulation to the day
            self.op_ob.cumulative_dead[self.d] = self.tot_num_dead[self.t]                   # cumulative dead from start of simulation to the day
            self.op_ob.cumulative_new_inf_plot[self.d] = self.tot_num_new_inf[self.t]        # cumulative new infection from start of simulation to the day
            
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
                                                    
            self.d += 1
    

    # Function to calculate immediate reward /cost
    # Input parameter:
    # NULL
    def calc_imm_reward(self):
        million = 1000000 # one million dollars
        
        self.calc_unemployment()
    
        tot_alive = self.tot_pop - self.tot_num_dead[self.t - 1]   # total number of alive people at time step (t - 1)
    
        # number of unemployed = total alive people at time step (t - 1) x labor force participation rate /100  
        #                        x unemployment rate / 100
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
        beta_sd = self.beta_min + (1 - self.a_sd) * (self.beta_max - self.beta_min)
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
                # number of new infection (S -> L)
                self.num_new_inf[self.t][risk][age] = pop_dis_b[0,0] * self.rate_array[0] * self.dt
        
        # the total number of diagnosis
        self.num_diag[self.t] = self.num_base_test[self.t] + self.num_trac_test[self.t] + self.num_uni_test[self.t]

        # update total number of diagnosis, hospitalizations and deaths
        self.tot_num_diag[self.t] = self.tot_num_diag[self.t - 1] + np.sum(self.num_diag[self.t])
        self.tot_num_hosp[self.t] = self.tot_num_hosp[self.t - 1] + np.sum(self.num_hosp[self.t])
        self.tot_num_dead[self.t] = self.tot_num_dead[self.t - 1] +np.sum(self.num_dead[self.t])
        self.tot_num_new_inf[self.t] = self.tot_num_dead[self.t - 1] + np.sum(self.num_new_inf[self.t])       
        self.num_diag_inf[self.t] = np.sum(self.pop_dist_sim[self.t,:,:,4:7])
        self.num_undiag_inf[self.t] = np.sum(self.pop_dist_sim[self.t,:,:,1:4])

    # Function to run the simulation until total number of diagnosis match with the first observed data
    # Input parameter
    # NULL
    def dryrun(self):

        # Initialzing simulation population distribution by age and risk
        for risk in range(self.tot_risk):
            for age in range (self.tot_age):
                self.pop_dist_sim[self.t, risk, age, 0] = self.init_pop_dist[age, risk + 1]

        # Randomly assign risk and age to latent compartment ###### wont't it change the results???
        risk = 1
        age = 50

        # Start with only one person in latent period until the total number of diagnosis match with first reported case
        self.pop_dist_sim[self.t, risk, age, 1] = 1 # L compartment
        for i in range(2, self.num_state):
            self.pop_dist_sim[self.t, risk, age, i] = 0  # E I Q_L Q_E Q_I H R D compartments
        self.pop_dist_sim[self.t, risk, age, 0] = self.pop_dist_sim[self.t, risk, age, 0] - np.sum(self.pop_dist_sim[self.t, risk, age, 1: self.num_state]) 
 
        while(self.tot_num_diag[self.t] < self.dry_run_end_diag):  
            self.t += 1
            self.simulation_base()

    # Function to run the simulation until the last day of observed data
    # Input parameter:
    # None
    def sim_bf_rl_dry_run(self):
        # print('sim before rl dry run begins')
        t = 1
        # simulate before social distancing measures
        while t <= (self.days_of_simul_pre_sd * self.inv_dt):
            self.t += 1
            self.step(action_t = np.array([0, 0, 0]))
            
            t += 1
      
        t = 1
        # simulate after social distancing measure
        while t <=  (self.days_of_simul_post_sd * self.inv_dt):
            self.t += 1
            self.step(action_t = np.array([1, 0, 0]))
            t += 1
        
        
    # Function to intialize simulation, do dry run and any simulation before the decision making   
    # Input parameter:
    # NULL
    def init_sim(self):
        # print("reset_sim begin")
        self.d = 0
        self.t = 0  
        self.rate_array = np.zeros([16 ,1])     # initialize rate array
        
        ## Initialize measures for epidemics
        self.num_diag = np.zeros((self.T_total + 1, self.tot_risk, self.tot_age))        # number of diagnosis
        self.num_dead = np.zeros((self.T_total + 1, self.tot_risk, self.tot_age))        # number of deaths
        self.num_hosp = np.zeros((self.T_total + 1, self.tot_risk, self.tot_age))        # number of hospitalizations
        self.num_new_inf = np.zeros((self.T_total + 1, self.tot_risk, self.tot_age))     # number of newly infection   
        
        self.pop_dist_sim = np.zeros((self.T_total + 1, self.tot_risk, \
                                      self.tot_age, self.num_state))                     # population distribution by risk, age and epidemic state

        self.num_base_test = np.zeros((self.T_total + 1, self.tot_risk, self.tot_age))   # number of diagnosed through symptom-based testing 
        self.num_uni_test = np.zeros((self.T_total + 1, self.tot_risk, self.tot_age))    # number of diagnosed through universal testing
        self.num_trac_test = np.zeros((self.T_total + 1, self.tot_risk, self.tot_age))   # number of diagnosed through contact tracing

        self.tot_num_diag = np.zeros(self.T_total + 1)                                   # cumulative diagnosed
        self.tot_num_dead = np.zeros(self.T_total + 1)                                   # cumulative deaths
        self.tot_num_hosp = np.zeros(self.T_total + 1)                                   # cumulative hospitalizations
        self.tot_num_new_inf = np.zeros(self.T_total + 1)                                # cumulative new infections (S-> L)
        self.num_diag_inf = np.zeros(self.T_total + 1)                                   # Q_L + Q_E + Q_I
        self.num_undiag_inf = np.zeros(self.T_total + 1)                                 # L + E + I

        # initialize action
        self.a_sd = 0
        self.a_c = 0
        self.a_u = 0
        self.T_c = 0
        self.T_u = 0

        # print("reset rl begin")
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
        # print("reset rl end")

        # after dry run, total number of diagnosis should match with data 
        self.dryrun()   
        
        # re-initialize all the below parameters
        self.pop_dist_sim[0] = self.pop_dist_sim[self.t]
        self.num_diag[0] = self.num_diag[self.t]
        self.num_hosp[0] = self.num_hosp[self.t]
        self.num_dead[0] = self.num_dead[self.t]
        self.num_new_inf[0] = self.num_new_inf[self.t]
        self.tot_num_diag[0] = self.tot_num_diag[self.t]
        self.tot_num_dead[0] = self.tot_num_dead[self.t]
        self.tot_num_hosp[0] = self.tot_num_hosp[self.t]
        self.tot_num_new_inf[0] = self.tot_num_new_inf[self.t]
        self.num_base_test[0] = self.num_base_test[self.t]
        self.num_uni_test[0] = self.num_uni_test[self.t]
        self.num_trac_test[0] = self.num_trac_test[self.t]
        self.num_diag_inf[0] = self.num_diag_inf[self.t]
        self.num_undiag_inf[0] = self.num_undiag_inf[self.t]
        self.policy[0] =  self.policy[self.t]
        self.rate_unemploy[0] = gv.init_unemploy        # assign initial unemployment rate     
        
        # reset time
        self.t = 0
        self.output_result()
        self.sim_bf_rl_dry_run()                             # rl dry run until current observed data
                         
        # print("reset_sim end")
        


def run_COVID_sim(decision = None):
    sample_model = CovidModel()
   
    # This dictionary will output necessary results for further simulation
    dic = {'self.pop_dist_sim': sample_model.pop_dist_sim[sample_model.t].tolist(),
            'self.num_diag': sample_model.num_diag[sample_model.t].tolist(),
            'self.num_hosp': sample_model.num_hosp[sample_model.t].tolist(),
            'self.num_dead': sample_model.num_dead[sample_model.t].tolist(),
            'self.num_new_inf': sample_model.num_new_inf[sample_model.t].tolist(),
            'self.num_base_test': sample_model.num_base_test[sample_model.t].tolist(),
            'self.num_uni_test': sample_model.num_uni_test[sample_model.t].tolist(),
            'self.num_trac_test': sample_model.num_trac_test[sample_model.t].tolist(),
            'self.tot_num_diag': sample_model.tot_num_diag[sample_model.t],
            'self.tot_num_dead': sample_model.tot_num_dead[sample_model.t],
            'self.tot_num_hosp': sample_model.tot_num_hosp[sample_model.t],
            'self.tot_num_new_inf': sample_model.tot_num_new_inf[sample_model.t],
            'self.rate_unemploy': sample_model.rate_unemploy[sample_model.t],
            'self.next_start_day': gv.begin_decision_date.strftime("%m/%d/%Y")}         
    
    
    sample_model.op_ob.plot_cum_output(gv.actual_data)  # plot to see calibration comparison with acutal data (can be commented)
    # write all the results into Excel file for plotting purpose (further simualtion)
    sample_model.op_ob.write_output(gv.actual_data, gv.acutal_unemp)
    # write necessary results for further simulation purpose
    sample_model.op_ob.write_sim_result(var_to_save = dic) 

    print('Finished the run')

def main(state):
    inv_dt = 10                 # insert time steps within each day
    gv.setup_global_variables(state, inv_dt)
    run_COVID_sim()

if  __name__ == "__main__":
    # state_list = ["NM", "OH", "OK", "OR", "RI"]
    state_list = ["NY"] 
    for state in state_list:
        main(state)
    

    
    
    

    
