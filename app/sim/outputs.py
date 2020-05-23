import numpy as np
import matplotlib.pyplot as plt
from pylab import rcParams
import pdb

class output_var:

    def __init__(self,sizeofrun):

        self.time_step = np.empty(sizeofrun)
        self.action_plot = np.empty(sizeofrun)
        self.a_sd_plot = np.empty(sizeofrun)
        self.num_inf_plot = np.empty(sizeofrun)  #reported cases             
        self.num_hosp_plot = np.empty(sizeofrun)  #severe cases
        self.num_dead_plot = np.empty(sizeofrun)
        self.VSL_plot = np.empty(sizeofrun)
        self.SAL_plot = np.empty(sizeofrun)
        self.cumulative_inf = np.empty(sizeofrun)
        self.cumulative_hosp = np.empty(sizeofrun)
        self.cumulative_dead = np.empty(sizeofrun)
        self.unemployment = np.empty(sizeofrun)

        #return (time_step, action_plot, a_sd_plot, num_inf_plot, num_hosp_plot, 
            #num_dead_plot, VSL_plot, SAL_plot, cumulative_inf, cumulative_hosp, cumulative_dead)

    def plot_output(self):
        
        fig, ax = plt.subplots(2,2)
        ax[0,0].plot(self.time_step,self.VSL_plot, 'r.-',label="VSL")
        ax[0,0].set_title("VSL")
        ax[0,1].plot(self.time_step,self.num_dead_plot, 'g.-',label="num_dead")
        ax[0,1].set_title("num_dead")
        ax[1,0].plot(self.time_step,self.SAL_plot, 'b.-',label="SAL")
        ax[1,0].set_title("SAL")
        ax[1,1].plot(self.time_step,self.unemployment, 'k.-',label="unemployment")
        ax[1,1].set_title("unemployment")
   
        plt.show()

        

       