import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter
import pathlib 
import global_var_pre_dm as gv
import json

class output_var:

    def __init__(self, sizeofrun, state):
        self.time_step = np.zeros(sizeofrun)
        self.num_inf_plot = np.zeros(sizeofrun)              
        self.num_hosp_plot = np.zeros(sizeofrun)  
        self.num_dead_plot = np.zeros(sizeofrun)
        self.VSL_plot = np.zeros(sizeofrun)
        self.SAL_plot = np.zeros(sizeofrun)
        self.cumulative_inf = np.zeros(sizeofrun)
        self.cumulative_hosp = np.zeros(sizeofrun)
        self.cumulative_dead = np.zeros(sizeofrun)
        self.cumulative_new_inf_plot = np.zeros(sizeofrun)   
        self.unemployment = np.zeros(sizeofrun)
        self.univ_test_cost = np.zeros(sizeofrun)
        self.trac_test_cost = np.zeros(sizeofrun)
        self.bse_test_cost = np.zeros(sizeofrun)
        self.num_base = np.zeros(sizeofrun)
        self.num_uni = np.zeros(sizeofrun)
        self.num_trac = np.zeros(sizeofrun)
        self.policy_plot = np.zeros((sizeofrun, 3))
        self.num_diag_inf = np.zeros(sizeofrun)
        self.num_undiag_inf = np.zeros(sizeofrun)
        self.num_new_inf_plot = np.zeros(sizeofrun)
        
        # new plots for scenario analysis:
        self.T_c_plot = np.zeros(sizeofrun)
        self.tot_test_cost_plot = np.zeros(sizeofrun)

        self.State = state
        date_result = gv.read_date(self.State)
        self.start_d =  date_result[0]

        self.date_range = pd.date_range(start= self.start_d, periods= sizeofrun, freq = 'D')
        self.dpi = 150
        
    def write_sim_result(self, var_to_save):
        json_path = gv.path_home /'data'/'results'/'{0}_sim_results.json'.format(self.State)
        with open(json_path, 'w') as fp:
            json.dump(var_to_save, fp)

    def write_output(self, actual_data, actual_unemploy):
        excel_path = gv.path_home /'data'/'results'/'{0}_sim_results.xlsx'.format(self.State)
        writer = pd.ExcelWriter(excel_path, engine = 'xlsxwriter')

        # Sheet 1
        df1 = pd.DataFrame({'Date': self.date_range,
                           'Value of statistical life-year (VSL) loss': self.VSL_plot,
                           'Number of new deaths': self.num_dead_plot})
        df1.to_excel(writer, sheet_name = 'VSL')

        # Sheet 2 
        df2 = pd.DataFrame({'Date': self.date_range,
                           'Wage loss': self.SAL_plot,
                           'Unemployment rate assumption under selected social distancing':self.unemployment})
        df2.to_excel(writer, sheet_name = 'Unemployment')
        
        # Sheet 3 
        df3 = pd.DataFrame({'Date': self.date_range,
                           'cost of universal testing': self.univ_test_cost,
                           'cost of contact tracing':self.trac_test_cost,
                           'cost of symptom-based testing': self.bse_test_cost,
                           'total cost of testing': self.tot_test_cost_plot,
                           'number of new diagnosis through contact tracing': self.num_trac,
                           'number of new diagnosis through symptom-based testing': self.num_base,
                           'number of new diagnosis through universal testing':self.num_uni,
                           'number of contact tracing test needed': self.T_c_plot})
        df3.to_excel(writer, sheet_name = 'Testing')

         # Sheet 4 
        df4 = pd.DataFrame({'Date': self.date_range,
                           'Percent reduction in contacts through social distancing': self.policy_plot[:, 0],
                           'Testing capacity – maximum tests per day through contact tracing': self.policy_plot[:, 1],
                           'Testing capacity – maximum tests per day through universal testing': self.policy_plot[:, 2]})
        df4['Percent reduction in contacts through social distancing'] = df4['Percent reduction in contacts through social distancing'].astype(int)
        df4['Testing capacity – maximum tests per day through universal testing'] = df4['Testing capacity – maximum tests per day through universal testing'].astype(int)
        df4.to_excel(writer, sheet_name = 'Decision choice')

        # Sheet 5 
        df5 = pd.DataFrame({'Date': self.date_range,
                           'simulated cumulative diagnosis': self.cumulative_inf,
                           'simulated cumulative hospitalized': self.cumulative_hosp,
                           'simulated cumulative deaths': self.cumulative_dead,
                           'number of infected, diagnosed': self.num_diag_inf,
                           'number of infected, undiagnosed': self.num_undiag_inf,
                           'number of new infection': self.num_new_inf_plot,
                           'cumulative new infection': self.cumulative_new_inf_plot})
        df5.to_excel(writer, sheet_name = 'Summary')
        
        # Sheet 6 and Sheet 7
        actual_data.to_excel(writer, sheet_name = 'Actual epidemic data')
        actual_unemploy.to_excel(writer, sheet_name = 'Actual unemployment rate')
        writer.save()
     
    

    # Plot epidimic data
    def plot_cum_output(self, actual_data): 
        # transform actual data
        actual_data['Date'] = actual_data.index

        # style use
        plt.style.use('seaborn')

        df = pd.DataFrame({'Date': self.date_range,
                           'simulated cumulative diagnosis': self.cumulative_inf,
                           'simulated cumulative hospitalized': self.cumulative_hosp,
                           'simulated cumulative deaths': self.cumulative_dead,
                           'number of infected, diagnosed': self.num_diag_inf,
                           'number of infected, undiagnosed': self.num_undiag_inf})

        # first subplot: cumulative diagnosis
        fig, ax = plt.subplots(3, 1, sharex = True)
        df.plot(x = 'Date', y = 'simulated cumulative diagnosis', fontsize = 10, ax = ax[0])
        actual_data.plot(x = 'Date', y = 'actual cumulative diagnosis', fontsize = 10, ax = ax[0])
        ax[0].yaxis.set_major_formatter(FuncFormatter(lambda x, p: format(int(x), ','))) 
        ax[0].set_title("Cumulative diagnosis")

        # second subplot: cumulative deaths
        df.plot(x = 'Date', y = 'simulated cumulative deaths', fontsize = 10, ax = ax[1])
        actual_data.plot(x = 'Date', y = 'actual cumulative deaths', fontsize = 10, ax = ax[1])
        ax[1].yaxis.set_major_formatter(FuncFormatter(lambda x, p: format(int(x), ','))) 
        ax[1].set_title("Cumulative deaths")
       

        # third subplot: cumulative hospitalization
        df.plot(x = 'Date', y = 'simulated cumulative hospitalized', fontsize = 10, ax = ax[2])
        actual_data.plot(x = 'Date', y = 'actual cumulative hospitalized', fontsize = 10, ax = ax[2])
        ax[2].yaxis.set_major_formatter(FuncFormatter(lambda x, p: format(int(x), ','))) 
        ax[2].set_title("Cumulative hospitalizations")

        plt.subplots_adjust(hspace = 0.4)
        figure_path = gv.path_home /'results'/'{0}_epi.png'.format(self.State)
        plt.savefig(figure_path, dpi = self.dpi)
        plt.close()

        """ # plot second graph: number of people with infection
        fig1, ax1 = plt.subplots()
        df.plot(x = 'Date', y = 'number of infected, diagnosed', fontsize = 10, ax = ax1)
        df.plot(x = 'Date', y = 'number of infected, undiagnosed', fontsize = 10, ax = ax1)
        ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, p: format(int(x), ','))) 
        plt.title("Number of people with infection on that day")
        plt.savefig('5.png',dpi = self.dpi)"""


    
    """
    # plot summary result    
    def plot_subplots(self):
        plt.style.use('seaborn')
        date = pd.date_range(start= self.start_d, periods= self.num_inf_plot.shape[0])
        df_data = np.array([date, self.num_inf_plot, self.num_dead_plot, \
                           self.cumulative_inf, self.cumulative_dead,\
                           self.num_diag_inf, self.num_undiag_inf])
        df_name = ['date', 'number of new diagnosis','number of new deaths', \
                   'cumualtive diagnosis', 'cumulative deaths',\
                   'number of infected, diagnosed', 'number of infected, undiagnosed']
        df = pd.DataFrame(data = df_data.T, index = None, columns = df_name)

        color_set = sns.color_palette(n_colors=6)
        fig, ax = plt.subplots(2, 3, sharex=True)
        
        df.plot(x = 'date', y = 'number of new diagnosis', legend = False, fontsize = 8, ax = ax[0][0], c=color_set[0])
        df.plot(x = 'date', y = 'number of new deaths', legend = False, fontsize = 8, ax = ax[0][1], c=color_set[1])
        df.plot(x = 'date', y = 'cumualtive diagnosis', legend = False, fontsize = 8, ax = ax[1][0], c=color_set[2])
        df.plot(x = 'date', y = 'cumulative deaths', legend = False, fontsize = 8, ax = ax[1][1], c=color_set[3])
        df.plot(x = 'date', y = 'number of infected, diagnosed', legend = False, fontsize = 8, ax = ax[0][2], c=color_set[4])
        df.plot(x = 'date', y = 'number of infected, undiagnosed',legend = False, fontsize = 8, ax = ax[1][2], c=color_set[5])

        ax[0][0].set_title("Number of new diagnosis per day", fontsize = 8)
        ax[0][1].set_title("Number of new deaths per day", fontsize = 8)
        ax[1][0].set_title("Cumulative diagnosis", fontsize = 8)
        ax[1][1].set_title("Cumulative deaths", fontsize = 8)
        ax[0][2].set_title("Number of people with infection, diagnosed", fontsize = 8)
        ax[1][2].set_title("Number of people with infection, undiagnosed", fontsize = 8)

        ax[1][0].set_xlabel("Date", fontsize = 8)
        ax[1][1].set_xlabel("Date", fontsize = 8)
        ax[1][2].set_xlabel("Date", fontsize = 8)"""


