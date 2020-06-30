
# Good source for annotation: http://members.cbio.mines-paristech.fr/~nvaroquaux/tmp/matplotlib/examples/pylab_examples/annotation_demo2.html
import numpy as np
#import matplotlib.pyplot as plt
import pandas as pd
#from matplotlib.ticker import FuncFormatter
#import seaborn as sns
#import ImageMerge as im


class output_var:

    def __init__(self, sizeofrun, state, start_d, decision_d):
        self.time_step = np.zeros(sizeofrun)
        self.action_plot = np.zeros(sizeofrun)
        self.a_sd_plot = np.zeros(sizeofrun)
        self.num_inf_plot = np.zeros(sizeofrun)  #reported cases
        self.num_hosp_plot = np.zeros(sizeofrun)  #severe cases
        self.num_dead_plot = np.zeros(sizeofrun)
        self.VSL_plot = np.zeros(sizeofrun)
        self.SAL_plot = np.zeros(sizeofrun)
        self.cumulative_inf = np.zeros(sizeofrun)
        self.cumulative_hosp = np.zeros(sizeofrun)
        self.cumulative_dead = np.zeros(sizeofrun)
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

        # new plots for scenario analysis:
        self.T_c_plot = np.zeros(sizeofrun)
        self.tot_test_cost_plot = np.zeros(sizeofrun)

        # define some parameters for plotting
        self.State = state
        self.start_d = start_d
        self.decision_d = decision_d

        self.date_range = pd.date_range(start= self.start_d, periods= sizeofrun, freq = 'D')

        self.dpi = 300 # figure dpi


    # write results from current simulation to a new DataFrame
    def write_current_results(self):

        df1 = pd.DataFrame({'Date': self.date_range,
                           'Value of statistical life-year (VSL) loss': self.VSL_plot,
                           'Number of new deaths': self.num_dead_plot})

        df2 = pd.DataFrame({'Date': self.date_range,
                           'Wage loss': self.SAL_plot,
                           'Unemployment rate assumption under selected social distancing':self.unemployment})

        df3 = pd.DataFrame({'Date': self.date_range,
                           'cost of universal testing': self.univ_test_cost,
                           'cost of contact tracing':self.trac_test_cost,
                           'cost of symptom-based testing': self.bse_test_cost,
                           'total cost of testing': self.tot_test_cost_plot,
                           'number of new diagnosis through contact tracing': self.num_trac,
                           'number of new diagnosis through symptom-based testing': self.num_base,
                           'number of new diagnosis through universal testing':self.num_uni,
                           'number of contact tracing test needed': self.T_c_plot})


        df4 = pd.DataFrame({'Date': self.date_range,
                           'Percent reduction in contacts through social distancing': self.policy_plot[:, 0],
                           'Testing capacity – maximum tests per day through contact tracing': self.policy_plot[:, 1],
                           'Testing capacity – maximum tests per day through universal testing': self.policy_plot[:, 2]})
        # df4['Percent reduction in contacts through social distancing'] = df4['Percent reduction in contacts through social distancing'].astype(int)
        # df4['Testing capacity – maximum tests per day through universal testing'] = df4['Testing capacity – maximum tests per day through universal testing'].astype(int)

        df5 =  pd.DataFrame({'Date': self.date_range,
                           'simulated cumulative diagnosis': self.cumulative_inf,
                           'simulated cumulative hospitalized': self.cumulative_hosp,
                           'simulated cumulative deaths': self.cumulative_dead,
                           'number of infected, diagnosed': self.num_diag_inf,
                           'number of infected, undiagnosed': self.num_undiag_inf,
                           'number of contact tracing test needed': self.T_c_plot})

        return df1, df2, df3, df4, df5


    # Function to combine previous simulation results and current simulation
    # results together to one single Excel file with categorized sheets
    def write_output(self, pre_results):

        df1_c, df2_c, df3_c, df4_c, df5_c = self.write_current_results()

        df1 = pre_results.parse(sheet_name='VSL', index_col = 0)
        df1 = df1.append(df1_c, ignore_index=True)

        df2 = pre_results.parse(sheet_name='Unemployment', index_col = 0)
        df2 = df2.append(df2_c, ignore_index=True)

        df3 = pre_results.parse(sheet_name= 'Testing', index_col = 0)
        df3 = df3.append(df3_c, ignore_index=True)

        df4 = pre_results.parse(sheet_name='Decision choice', index_col = 0)
        df4 = df4.append(df4_c, ignore_index=True)

        df5 = pre_results.parse(sheet_name='Summary', index_col = 0)
        df5 = df5.append(df5_c, ignore_index=True)

        actual_data = pre_results.parse(sheet_name ='Actual epidemic data', index_col = 0)
        actual_unemp = pre_results.parse(sheet_name ='Actual unemployment rate', index_col = 0)

        # write to a new file
        writer = pd.ExcelWriter('{0}_final_result.xlsx'.format(self.State), engine = 'xlsxwriter')

        df1.to_excel(writer, sheet_name = 'VSL')
        df2.to_excel(writer, sheet_name = 'Unemployment')
        df3.to_excel(writer, sheet_name = 'Testing')
        df4.to_excel(writer, sheet_name = 'Decision choice')
        df5.to_excel(writer, sheet_name = 'Summary')

        writer.save()
        return df1, df2, df3, df4, df5, actual_data, actual_unemp


    # Plot all the results for single run
    def plot_results(self, df_l):
        # define data
        df1 = df_l[0]
        df2 = df_l[1]
        df3 = df_l[2]
        df4 = df_l[3]
        df5 = df_l[4]
        actual_data = df_l[5]
        actual_unemp = df_l[6]

        # create annotation style
        text = 'Start decision-making'
        bbox= dict(boxstyle='round', fc = 'yellow', alpha = 0.3)
        arrowprops = dict(arrowstyle = "->")
        size = 9
        plt.style.use('seaborn')

        ################ first graph ##############
        # define figure and axes
        fig, ax = plt.subplots(2, 1, sharex = True)

        # first subplot: number of deaths
        df1.plot(x = 'Date', y = 'Number of new deaths', title = 'Number of new deaths per day', ax = ax[0], \
                legend = False, fontsize = 10, color ='r')

        # second subplot: VSL
        df1.plot(x = 'Date', y = 'Value of statistical life-year (VSL) loss',\
                title = 'Value of statistical life-year (VSL) loss per day', \
                ax = ax[1], legend = False, fontsize = 10)
        ax[1].set_ylabel("US dollars (in millions)")

        # adjust subplot space
        plt.subplots_adjust(hspace = 0.2)

        # add thousand sign
        ax[0].yaxis.set_major_formatter(FuncFormatter(lambda x, p: format(int(x), ',')))
        ax[1].yaxis.set_major_formatter(FuncFormatter(lambda x, p: format(int(x), ',')))

        # add annotation
        is_date = df1.loc[df1['Date']== pd.to_datetime(self.decision_d)]
        y1 = is_date['Number of new deaths']
        ax[0].annotate(text,(self.decision_d, y1),xytext = (60, 30), \
                        textcoords='offset points', size = size,\
                        bbox = bbox, arrowprops = arrowprops)

        y2 = is_date['Value of statistical life-year (VSL) loss']
        ax[1].annotate(text,(self.decision_d, y2),xytext = (60, 30), \
                      textcoords='offset points', size = size,\
                      bbox = bbox, arrowprops = arrowprops)

        plt.savefig('1.png',dpi = self.dpi)
        plt.close()


        ############### second graph #################
        # define figure and axes
        fig, ax = plt.subplots(2, 1, sharex = True)
        day = pd.Timestamp(self.decision_d)

        # first subplot: assumpation of unemployment rate and actual unemployment rate
        df2.loc[df2['Date'] >= day].plot(x = 'Date', y = 'Unemployment rate assumption under selected social distancing',
                ax = ax[0], fontsize = 10, marker= '.', linestyle = '--')

        actual_unemp.plot(x = 'Date', y = 'Actual unemployment rate', ax = ax[0], fontsize = 10,marker= '.',\
                          label = 'Actual unemployment rate')
        ax[0].set_title('Unemployment rate \n (Assumption: Assumption for unemployment rate under selected social distancing)')
        ax[0].yaxis.set_major_formatter(FuncFormatter(lambda y, _: '{:.0%}'.format(y)))

        # second subplot: wage loss over time
        df2.loc[df2['Date'] >= day].plot(x = 'Date', y = 'Wage loss', title = 'Wage loss per day', \
                                                  ax = ax[1], legend = False, fontsize = 10,\
                                                  marker= '.', linestyle = '--')
        ax[1].set_ylabel("US dollars (in millions)")
        sim_start_d = df2['Date'].iloc[0]
        ax[1].set_xlim(left = sim_start_d)


        # add annotation
        is_date = df2.loc[df2['Date']== pd.to_datetime(self.decision_d)]
        y1 = is_date['Unemployment rate assumption under selected social distancing']
        ax[0].annotate(text,(self.decision_d,y1),xytext= (-40, -30), \
                        textcoords='offset points',size = size,\
                        bbox = bbox, arrowprops = arrowprops)

        y2 = is_date['Wage loss']
        ax[1].annotate(text,(self.decision_d,y2),xytext=  (-90, -30), \
                        textcoords='offset points',size = size,\
                        bbox = bbox, arrowprops = arrowprops)

        # save figure and close
        plt.savefig('2.png', dpi = self.dpi)
        plt.close()

        ######## third graph #########
        # plot subplot
        fig, ax = plt.subplots(2, 1, sharex = True)

        # first subplot: number of diagnosed by testing type
        day = pd.Timestamp(self.decision_d)
        df3.loc[df3['Date'] >= day].plot(x = 'Date', y = 'number of new diagnosis through universal testing',  ax = ax[0], fontsize = 10)
        df3.loc[df3['Date'] >= day].plot(x = 'Date', y = 'number of new diagnosis through contact tracing', ax = ax[0], fontsize = 10)
        df3.plot(x = 'Date', y = 'number of new diagnosis through symptom-based testing', ax = ax[0], fontsize = 10)
        ax[0].set_title("Number of new diagnosis through testing type per day")
        ax[0].yaxis.set_major_formatter(FuncFormatter(lambda x, p: format(int(x), ',')))

        # second subplot: cost of testing by testing type
        df3.loc[df3['Date'] >= day].plot(x = 'Date', y = 'cost of universal testing', ax = ax[1], fontsize = 10)
        df3.loc[df3['Date'] >= day].plot(x = 'Date', y = 'cost of contact tracing', ax = ax[1], fontsize = 10)
        df3.plot(x = 'Date', y = 'cost of symptom-based testing', ax = ax[1], fontsize = 10)
        ax[1].set_ylabel("US dollars (in millions)")
        ax[1].set_title("Cost of testing by type per day")

        ax[0].annotate(text,(self.decision_d,0),xytext= (-90, -30), \
                        textcoords='offset points', size = size,\
                        bbox = bbox, arrowprops = arrowprops)
        ax[1].annotate(text,(self.decision_d,0),xytext= (-90, -30), \
                        textcoords='offset points',size = size,\
                        bbox = bbox, arrowprops = arrowprops)

        # adjust subplot
        plt.subplots_adjust(hspace = 0.5, wspace = 0.5)
         # save figure and close
        plt.savefig('3.png',dpi = self.dpi)
        plt.close()

        ######### forth graph #############
        # plot subplot
        fig, ax = plt.subplots(2, 1, sharex = True)

        # first subplot: contact decision
        df4.plot(x = 'Date', y ='Percent reduction in contacts through social distancing', \
               label = 'User entered decision choice for: \nPercent reduction in contacts through social distancing', \
               fontsize = 10, marker='.', ax = ax[0], c = 'k')
        # ax[0].set_xlim(left = self.start_d)
        ax[0].set_ylim(bottom = 0, top = 1)
        ax[0].yaxis.set_major_formatter(FuncFormatter(lambda y, _: '{:.0%}'.format(y)))
        ax[0].set_ylabel('Proportion')

        # second subplot: testing decision
        df4.plot(x = 'Date', y ='Testing capacity – maximum tests per day through contact tracing', \
               label = 'User entered decision choice for: \nTesting capacity – maximum tests per day through contact tracing', \
               fontsize = 10, marker='.',ax = ax[1])
        df4.plot(x = 'Date', y ='Testing capacity – maximum tests per day through universal testing', \
               label = 'User entered decision choice for: \nTesting capacity – maximum tests per day through universal testing', \
               fontsize = 10, marker='.',ax = ax[1])
        # ax[1].set_xlim(left = sim_start_d)
        ax[1].set_ylim(bottom = 0)
        ax[1].yaxis.set_major_formatter(FuncFormatter(lambda x, p: format(int(x), ',')))
        ax[1].set_ylabel('Testing capacity')

        # add annotation
        is_date = df4.loc[df4['Date']== pd.to_datetime(self.decision_d)]
        y1 = is_date['Percent reduction in contacts through social distancing']
        ax[0].annotate(text,(self.decision_d, y1),xytext=(-90, 30), \
                        textcoords='offset points',size = size,\
                        bbox = bbox, arrowprops = arrowprops)

        y2 = is_date['Testing capacity – maximum tests per day through contact tracing']
        ax[1].annotate(text,(self.decision_d, y2),xytext=(-90, 30), \
                       textcoords='offset points',size = size,\
                        bbox = bbox, arrowprops = arrowprops)

        # title
        fig.suptitle('User entered decision choice')
        plt.savefig('4.png',dpi = self.dpi)
        plt.close()

        ######### fifth graph #############

        # first subplot: cumulative diagnosis
        fig, ax = plt.subplots()
        df5.plot(x = 'Date', y = 'simulated cumulative diagnosis', fontsize = 10, ax = ax)
        actual_data.plot(x = 'Date', y = 'actual cumulative diagnosis', fontsize = 10, ax = ax)
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: format(int(x), ',')))
        ax.set_title("Cumulative diagnosis")
        plt.savefig('5.png',dpi = self.dpi)
        plt.close


        # second subplot: cumulative deaths
        fig, ax = plt.subplots()
        df5.plot(x = 'Date', y = 'simulated cumulative deaths', fontsize = 10, ax = ax)
        actual_data.plot(x = 'Date', y = 'actual cumulative deaths', fontsize = 10, ax = ax)
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: format(int(x), ',')))
        ax.set_title("Cumulative deaths")
        plt.savefig('6.png',dpi = self.dpi)
        plt.close


        # third subplot: cumulative hospitalization
        fig, ax = plt.subplots()
        df5.plot(x = 'Date', y = 'simulated cumulative hospitalized', fontsize = 10, ax = ax)
        actual_data.plot(x = 'Date', y = 'actual cumulative hospitalized', fontsize = 10, ax = ax)
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: format(int(x), ',')))
        ax.set_title("Cumulative hospitalizations")
        plt.savefig('7.png',dpi = self.dpi)
        plt.close


        # forth subplot: number of people with infection
        fig, ax = plt.subplots()
        df5.plot(x = 'Date', y = 'number of infected, diagnosed', fontsize = 10, ax = ax)
        df5.plot(x = 'Date', y = 'number of infected, undiagnosed', fontsize = 10, ax = ax)
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: format(int(x), ',')))
        ax.set_title("Number of people with infection on the day")
        plt.savefig('8.png',dpi = self.dpi)
        plt.close

        # # plt.savefig('{0}_epi.png'.format(self.State), dpi = self.dpi)
        # plt.savefig('Results.png', dpi = self.dpi)
        # plt.close()

        ### merge images ####
        im.merge_image()


    # Function to output scenario analysis needed results - Excel sheet
    def write_scenario_needed_results(self, pre_results):
        df1_c, df2_c, df3_c, df4_c, df5_c = self.write_current_results()

        df1 = pre_results.parse(sheet_name='VSL', index_col = 0)
        df1 = df1.append(df1_c, ignore_index=True)

        df2 = pre_results.parse(sheet_name='Unemployment', index_col = 0)
        df2 = df2.append(df2_c, ignore_index=True)

        df3 = pre_results.parse(sheet_name= 'Testing', index_col = 0)
        df3 = df3.append(df3_c, ignore_index=True)

        df4 = pre_results.parse(sheet_name='Decision choice', index_col = 0)
        df4 = df4.append(df4_c, ignore_index=True)

        df5 = pre_results.parse(sheet_name='Summary', index_col = 0)
        df5 = df5.append(df5_c, ignore_index=True)

        # Combine the data you needed for plotting scenario analysis
        data = [df1['Date'],
                df1['Value of statistical life-year (VSL) loss'],\
                df2['Wage loss'],
                df3['total cost of testing'],  # C_u + C_c + C_b
                df3['number of contact tracing test needed'], # T_c
                df5['number of infected, undiagnosed'],  # L + E + I
                df5['number of infected, diagnosed']]  # Q_L + Q_E + Q_I

        headers = ['Date', 'Value of statistical life-year (VSL) loss',\
                   'Wage loss', 'total cost of testing','number of contact tracing test needed',\
                   'number of infected, undiagnosed', 'number of infected, diagnosed']

        df = pd.concat(data, axis=1, keys=headers)

        return df


    # Function to output scenario analysis needed results - Colab
    def write_scenario_needed_results_colab(self, pre_results):
        df1_c, df2_c, df3_c, df4_c, df5_c = self.write_current_results()

        df1 = pre_results.parse(sheet_name='VSL', index_col = 0)
        df1 = df1.append(df1_c, ignore_index=True)

        df2 = pre_results.parse(sheet_name='Unemployment', index_col = 0)
        df2 = df2.append(df2_c, ignore_index=True)

        df3 = pre_results.parse(sheet_name= 'Testing', index_col = 0)
        df3 = df3.append(df3_c, ignore_index=True)

        df4 = pre_results.parse(sheet_name='Decision choice', index_col = 0)
        df4 = df4.append(df4_c, ignore_index=True)

        df5 = pre_results.parse(sheet_name='Summary', index_col = 0)
        df5 = df5.append(df5_c, ignore_index=True)

        # Combine the data you needed for plotting scenario analysis
        data = [df1['Date'],
                df1['Value of statistical life-year (VSL) loss'],\
                df1['Number of new deaths'],\
                df2['Wage loss'],
                df2['Unemployment rate assumption under selected social distancing'],\
                df3['cost of universal testing'],\
                df3['cost of contact tracing'],\
                df3['cost of symptom-based testing'],\
                df3['total cost of testing'],  # C_u + C_c + C_b
                df3['number of new diagnosis through contact tracing'],\
                df3['number of new diagnosis through symptom-based testing'],\
                df3['number of new diagnosis through universal testing'], \
                df4['Percent reduction in contacts through social distancing'],\
                df4['Testing capacity – maximum tests per day through contact tracing'],\
                df4['Testing capacity – maximum tests per day through universal testing'],\
                df5['number of infected, undiagnosed'],  # L + E + I
                df5['number of infected, diagnosed'], # Q_L + Q_E + Q_I
                df5['simulated cumulative diagnosis'],
                df5['simulated cumulative hospitalized'],
                df5['simulated cumulative deaths']]

        headers = ['Date', 'Value of statistical life-year (VSL) loss',\
                   'Number of new deaths', 'Wage loss', 'Unemployment rate assumption under selected social distancing',
                   'cost of universal testing', 'cost of contact tracing', 'cost of symptom-based testing',\
                   'total cost of testing','number of new diagnosis through contact tracing',\
                   'number of new diagnosis through symptom-based testing', 'number of new diagnosis through universal testing',\
                   'Percent reduction in contacts through social distancing', \
                   'Testing capacity – maximum tests per day through contact tracing', \
                   'Testing capacity – maximum tests per day through universal testing',
                   'number of infected, undiagnosed', 'number of infected, diagnosed',\
                   'simulated cumulative diagnosis', 'simulated cumulative hospitalized', 'simulated cumulative deaths']
        df = pd.concat(data, axis=1, keys=headers)

        return df, self.start_d, self.decision_d



    """
    # Plot unemployment rate and wage loss
    def plot_decision_output_1(self):
        # style use
        plt.style.use('seaborn')

        # create dataframe for VSL and number of new deaths
        df = pd.DataFrame({'Date': self.date_range,
                           'Value of statistical life-year (VSL) loss': self.VSL_plot,
                           'Number of new deaths': self.num_dead_plot})

        # plot subplot
        fig, ax = plt.subplots(2, 1, sharex = True)

        # first subplot: number of deaths
        df.plot(x = 'Date', y = 'Number of new deaths', title = 'Number of new deaths per day', ax = ax[0], \
                legend = False, fontsize = 10, color ='r')

        # second subplot: VSL
        df.plot(x = 'Date', y = 'Value of statistical life-year (VSL) loss',\
                title = 'Value of statistical life-year (VSL) loss per day', \
                ax = ax[1], legend = False, fontsize = 10)
        ax[1].set_ylabel("US dollars (in millions)")
        plt.subplots_adjust(hspace = 0.5)

        # create an arrow
        bbox = dict(boxstyle="round", fc="0.8")
        arrowprops = dict(arrowstyle = "->",connectionstyle = "angle,angleA=0,angleB=90,rad=5")
        offset = 72

        is_date = df.loc[df['Date']== pd.to_datetime(self.decision_d)]
        y1 = is_date['Number of new deaths']
        ax[0].annotate('Start of decision making',(self.decision_d, y1),xytext=(0.5*offset, 0.3*offset), \
          textcoords='offset points',bbox=bbox, arrowprops=arrowprops)

        y2 = is_date['Value of statistical life-year (VSL) loss']
        ax[1].annotate('Start of decision making',(self.decision_d, y2),xytext=(0.5*offset, 0.3*offset), \
          textcoords='offset points',bbox=bbox, arrowprops=arrowprops)

        # save figure and close
        plt.savefig('1.png',dpi = self.dpi)
        plt.close()

        return df


    # Plot unemloyment rate and wage loss
    def plot_decision_output_2(self, actual_unemp):
        # style use
        plt.style.use('seaborn')
        # create dataframe for unemloyment rate and wage loss
        df = pd.DataFrame({'Date': self.date_range,
                           'Wage loss': self.SAL_plot,
                           'Unemployment rate assumption under selected social distancing':self.unemployment})

        # plot subplot
        fig, ax = plt.subplots(2, 1, sharex = True)
        day = pd.Timestamp(self.decision_d)

        # first subplot: assumpation of unemployment rate and actual unemployment rate
        df.loc[df['Date'] >= day].plot(x = 'Date', y = 'Unemployment rate assumption under selected social distancing',
                ax = ax[0], fontsize = 10, marker= '.', linestyle = '--')

        actual_unemp.plot(x = 'Date', y = 'Actual unemployment rate', ax = ax[0], fontsize = 10,marker= '.',\
                          label = 'Actual unemployment rate')
        ax[0].set_title('Unemployment rate \n (Assumption: Assumption for unemployment rate under selected social distancing)')
        ax[0].yaxis.set_major_formatter(FuncFormatter(lambda y, _: '{:.0%}'.format(y)))

        # second subplot: wage loss over time
        df.loc[df['Date'] >= day].plot(x = 'Date', y = 'Wage loss', title = 'Wage loss per day', \
                                                  ax = ax[1], legend = False, fontsize = 10,\
                                                  marker= '.', linestyle = '--')
        ax[1].set_ylabel("US dollars (in millions)")
        ax[1].set_xlim(left = self.start_d)

        # create an arrow
        bbox = dict(boxstyle="round", fc="0.8")
        arrowprops = dict(arrowstyle = "->",connectionstyle = "angle,angleA=0,angleB=70,rad=5")
        offset = 72

        is_date = df.loc[df['Date']== pd.to_datetime(self.decision_d)]
        y1 = is_date['Unemployment rate assumption under selected social distancing']
        ax[0].annotate('Start of decision making',(self.decision_d,y1),xytext=(-0.3 * offset, -0.5*offset), \
                        textcoords='offset points',bbox=bbox, arrowprops=arrowprops)


        y2 = is_date['Wage loss']
        ax[1].annotate('Start of decision making',(self.decision_d,y2),xytext=(-0.5*offset, 0.5*offset), \
                        textcoords='offset points',bbox=bbox, arrowprops=arrowprops)

        # save figure and close
        plt.savefig('2.png', dpi = self.dpi)
        plt.close()

        return df

    # Plot new diagnosis and cost by testing type
    def plot_decision_output_3(self):
        # style use
        plt.style.use('seaborn')
        # create dataframe for new diagnosis and cost by testing type
        df = pd.DataFrame({'Date': self.date_range,
                           'cost of universal testing': self.univ_test_cost,
                           'cost of contact tracing':self.trac_test_cost,
                           'cost of symptom-based testing': self.bse_test_cost,
                           'diagnosed by contact tracing': self.num_trac,
                           'diagnosed by symptom-based testing': self.num_base,
                           'diagnosed by universal testing':self.num_uni})
        # plot subplot
        fig, ax = plt.subplots(2, 1, sharex = True)

        # first subplot: number of diagnosed by testing type
        day = pd.Timestamp(self.decision_d)
        df.loc[df['Date'] >= day].plot(x = 'Date', y = 'diagnosed by universal testing',  ax = ax[0], fontsize = 10)
        df.loc[df['Date'] >= day].plot(x = 'Date', y = 'diagnosed by contact tracing', ax = ax[0], fontsize = 10)
        df.plot(x = 'Date', y = 'diagnosed by symptom-based testing', ax = ax[0], fontsize = 10)
        ax[0].set_title("Number of new diagnosis by testing type per day")
        ax[0].yaxis.set_major_formatter(FuncFormatter(lambda x, p: format(int(x), ',')))

        # second subplot: cost of testing by testing type
        df.loc[df['Date'] >= day].plot(x = 'Date', y = 'cost of universal testing', ax = ax[1], fontsize = 10)
        df.loc[df['Date'] >= day].plot(x = 'Date', y = 'cost of contact tracing', ax = ax[1], fontsize = 10)
        df.plot(x = 'Date', y = 'cost of symptom-based testing', ax = ax[1], fontsize = 10)
        ax[1].set_ylabel("US dollars (in millions)")
        ax[1].set_title("Cost of testing by type per day")

        # create an arrow
        bbox = dict(boxstyle="round", fc = "0.8")
        arrowprops = dict(arrowstyle = "->",connectionstyle = "angle,angleA=0,angleB=70,rad=5")
        offset = 72


        ax[0].annotate('Start of decision making',(self.decision_d,0),xytext=(0.5*offset, 0.5*offset), \
                        textcoords='offset points', bbox=bbox, arrowprops=arrowprops)
        ax[1].annotate('Start of decision making',(self.decision_d,0),xytext=(0.5*offset, 0.5*offset), \
                        textcoords='offset points',bbox=bbox, arrowprops=arrowprops)

        # adjust subplot
        plt.subplots_adjust(hspace = 0.5, wspace = 0.5)
         # save figure and close
        plt.savefig('3.png',dpi = self.dpi)
        plt.close()
        return df

    # Plot epidimic data
    def plot_cum_output(self, actual_data):
        # transform actual data
        actual_data['Date'] = actual_data.index

        # style use
        plt.style.use('seaborn')
        # create dataframe for epidimic data
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
        ax[0].set_title("Cumulative diagnosis over time")

        # second subplot: cumulative deaths
        df.plot(x = 'Date', y = 'simulated cumulative deaths', fontsize = 10, ax = ax[1])
        actual_data.plot(x = 'Date', y = 'actual cumulative deaths', fontsize = 10, ax = ax[1])
        ax[1].yaxis.set_major_formatter(FuncFormatter(lambda x, p: format(int(x), ',')))
        ax[1].set_title("Cumulative deaths over time")


        # third subplot: cumulative hospitalization
        df.plot(x = 'Date', y = 'simulated cumulative hospitalized', fontsize = 10, ax = ax[2])
        actual_data.plot(x = 'Date', y = 'actual cumulative hospitalized', fontsize = 10, ax = ax[2])
        ax[2].yaxis.set_major_formatter(FuncFormatter(lambda x, p: format(int(x), ',')))
        ax[2].set_title("Cumulative hospitalizations over time")

        plt.subplots_adjust(hspace = 0.4)
        # plt.savefig('4.png', dpi = self.dpi)
        plt.savefig('{0}_epi.png'.format(self.State), dpi = self.dpi)
        plt.close()

        # plot second graph: number of people with infection
        fig1, ax1 = plt.subplots()
        df.plot(x = 'Date', y = 'number of infected, diagnosed', fontsize = 10, ax = ax1)
        df.plot(x = 'Date', y = 'number of infected, undiagnosed', fontsize = 10, ax = ax1)
        ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, p: format(int(x), ',')))
        plt.title("Number of people with infection on that day")
        plt.savefig('5.png',dpi = self.dpi)

        return df

    # Plot decision
    def plot_decison(self):
        # style use
        plt.style.use('seaborn')
        # create dataframe for testing decision and contact decision
        Date = pd.date_range(start= self.decision_d, periods= self.policy_plot.shape[0])
        df = pd.DataFrame({'Date': Date,
                           'Percent reduction in contacts through social distancing': self.policy_plot[:, 0],
                           'Testing capacity – maximum tests per day through contact tracing': self.policy_plot[:, 1],
                           'Testing capacity – maximum tests per day through universal testing': self.policy_plot[:, 2]})
        df['Percent reduction in contacts through social distancing'] = df['Percent reduction in contacts through social distancing'].astype(int)
        df['Testing capacity – maximum tests per day through universal testing'] = df['Testing capacity – maximum tests per day through universal testing'].astype(int)

        # plot subplot
        fig, ax = plt.subplots(2, 1, sharex = True)

        # first subplot: contact decision
        df.plot(x = 'Date', y ='Percent reduction in contacts through social distancing', \
               label = 'User entered decision choice for: \nPercent reduction in contacts through social distancing', \
               fontsize = 10, marker='.', ax = ax[0], c = 'k')
        # ax[0].set_xlim(left = self.start_d)
        ax[0].set_ylim(bottom = 0, top = 1)
        ax[0].yaxis.set_major_formatter(FuncFormatter(lambda y, _: '{:.0%}'.format(y)))
        ax[0].set_ylabel('Proportion')

        # second subplot: testing decision
        df.plot(x = 'Date', y ='Testing capacity – maximum tests per day through contact tracing', \
               label = 'User entered decision choice for: \nTesting capacity – maximum tests per day through contact tracing', \
               fontsize = 10, marker='.',ax = ax[1])
        df.plot(x = 'Date', y ='Testing capacity – maximum tests per day through universal testing', \
               label = 'User entered decision choice for: \nTesting capacity – maximum tests per day through universal testing', \
               fontsize = 10, marker='.',ax = ax[1])
        ax[1].set_xlim(left = self.start_d)
        ax[1].set_ylim(bottom = 0)
        ax[1].yaxis.set_major_formatter(FuncFormatter(lambda x, p: format(int(x), ',')))
        ax[1].set_ylabel('Testing capacity')

        # create an arrow
        bbox = dict(boxstyle="round", fc="0.8")
        arrowprops = dict(arrowstyle = "->",connectionstyle = "angle,angleA=0,angleB=70,rad=5")
        offset = 72

        is_date = df.loc[df['Date']== pd.to_datetime(self.decision_d)]
        y1 = is_date['Percent reduction in contacts through social distancing']
        ax[0].annotate('Start of decision making',(self.decision_d, y1),xytext=(-0.3*offset, -0.5*offset), \
                        textcoords='offset points',bbox=bbox, arrowprops=arrowprops)

        y2 = is_date['Testing capacity – maximum tests per day through contact tracing']
        ax[1].annotate('Start of decision making',(self.decision_d, y2),xytext=(-0.3*offset, 0.3*offset), \
                       textcoords='offset points',bbox=bbox, arrowprops=arrowprops)

        # title
        fig.suptitle('User entered decision choice')
        plt.savefig('6.png',dpi = self.dpi)
        plt.close()

        return df

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
        ax[1][0].set_title("Cumulative diagnosis over time", fontsize = 8)
        ax[1][1].set_title("Cumulative deaths over time", fontsize = 8)
        ax[0][2].set_title("Number of people with infection, diagnosed", fontsize = 8)
        ax[1][2].set_title("Number of people with infection, undiagnosed", fontsize = 8)

        ax[1][0].set_xlabel("Date", fontsize = 8)
        ax[1][1].set_xlabel("Date", fontsize = 8)
        ax[1][2].set_xlabel("Date", fontsize = 8)


    def plot_result(self, actual_unemp, actual_data, write):
        df1 = self.plot_decision_output_1()
        df2 = self.plot_decision_output_2(actual_unemp)
        df3 = self.plot_decision_output_3()
        df4 = self.plot_decison()
        df5 = self.plot_cum_output(actual_data)
        df = self.plot_(actual_unemp)
        # if write == 'Y' or write == 'y':
        #     self.write_output(df1, df2, df3, df4, df5)

    # Plot unemloyment rate and wage loss
    def plot_(self, actual_unemp):
        # style use
        plt.style.use('seaborn')
        # create dataframe for unemloyment rate and wage loss
        df = pd.DataFrame({'Date': self.date_range,
                           'Wage loss': self.SAL_plot,
                           'Unemployment rate assumption under selected social distancing':self.unemployment})

        # plot subplot
        fig, ax = plt.subplots(2, 1, sharex = True)

        # first subplot: assumpation of unemployment rate and actual unemployment rate
        df.plot(x = 'Date', y = 'Unemployment rate assumption under selected social distancing',
                ax = ax[0], fontsize = 10, marker= '.', linestyle = '--')

        actual_unemp.plot(x = 'Date', y = 'Actual unemployment rate', ax = ax[0], fontsize = 10,marker= '.',\
                          label = 'Actual unemployment rate')
        ax[0].set_title('Unemployment rate \n (Assumption: Assumption for unemployment rate under selected social distancing)')
        ax[0].yaxis.set_major_formatter(FuncFormatter(lambda y, _: '{:.0%}'.format(y)))

        # second subplot: wage loss over time
        df.plot(x = 'Date', y = 'Wage loss', title = 'Wage loss per day', \
                                                  ax = ax[1], legend = False, fontsize = 10,\
                                                  marker= '.', linestyle = '--')
        ax[1].set_ylabel("US dollars (in millions)")
        ax[1].set_xlim(left = self.start_d)


        # save figure and close
        plt.savefig('{0}_unemploy.png'.format(self.State), dpi = self.dpi)
        plt.close()

        return df"""
