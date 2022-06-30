from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
import math 

import sys
sys.path.insert(0, './')

from . import Constants as const
from . import util

#import Constants as const
#import util

class InfoGraph(object):
    def __init__(self):
        self.__xlabel= 'x'
        self.__ylabel = 'y'
        self.__title = 'title'
        self.__legend_config = 'upper center'
        
        self.__fig = plt.gcf()
    
    def __exit__(self):
        plt.close()
    
    @property
    def xlabel(self):
        return self.__xlabel
    
    @property
    def ylabel(self):
        return self.__ylabel

    @property
    def title(self):
        return self.__title
    
    @property
    def legend_config(self):
        return self.__legend_config
    
    
    def set_xlabel(self, value:str):
        self.__xlabel = value
        
    def set_ylabel(self, value:str):
        self.__ylabel = value
        
    def set_title(self, value:str):
        self.__title = value
        
    def set_legend_config(self, value:str):
        self.__legend_config = value
    
    def set_figure_size(self, new_size:list()):
        plt.rcParams['figure.figsize'] = new_size
    
    def __config_preset(self):
        plt.xlabel(self.__xlabel)
        plt.ylabel(self.__ylabel)
        plt.title(self.__title)   
    
    def __config_lastset(self):
        plt.legend(loc=self.__legend_config)
        
    
    def general_plot(self, xvals, yvals, label=None, method=plt.plot):
        self.__config_preset()
        
        if label is None: 
            label = self.__title     
        
        method(xvals, yvals, label=label)
        self.__config_lastset()
        
        self.__fig = plt.gcf()
    
    def plot(self, xvals, yvals, label:str=None):
        self.general_plot(xvals, yvals, label, plt.plot)
        
    def scatter(self, xvals, yvals, label:str=None):
        self.general_plot(xvals, yvals, label, plt.scatter)
        
    def bar(self, xvals, yvals, label:str=None):
        self.general_plot(xvals, yvals, label, plt.bar)
        
    def hbar(self, xvals, yvals, label:str=None):
        self.general_plot(xvals, yvals, label, plt.hbar)
        
    def hist(self, xvals, beans:int=None, label:str=None):
        self.__config_preset()
   
        if label is None: 
            label = self.__title     
        
        plt.hist(xvals, beans, label=label)
        self.__config_lastset()
        
        self.__fig = plt.gcf()
        
    def pie(self, xvals:list(), labels:list(), explode:list()=None):
        self.__config_preset()
        plt.pie(xvals, labels=labels, explode=explode)
        self.__config_lastset()
        
        self.__fig = plt.gcf()
         
    
    def fig(self)->plt.gcf():
        return self.__fig
        
    def show(self):
        #plt.show()
        plt.figure(self.__fig)
        plt.show()
        
    def save(self, path=None):
        if path is None:
            path = const.FIGURE_DATA_PATH
         
        util.resolve_sys_path(path)
         
        file = path + self.__title + '.png' 
        self.__fig.savefig(file, format='png')
        
if __name__ == '__main__':
    ig = InfoGraph()
    
    # teste 
    # caso 1:
    ig.set_figure_size([9, 7])
    x_vals = np.linspace(0, 20, 20)
    y_vals = [math.sqrt(i) for i in x_vals]
    
    ig.set_xlabel('x values')
    ig.set_ylabel('y values')
    ig.set_title('square roots')
    
    ig.plot(x_vals, y_vals, 'square root')
    
    #ig.set_legend_config('upper center')
    #ig.show()
    fig = ig.fig()
    ig.show()
    ig.save('t1')
    
    # caso 2:
    x_vals = np.linspace(0, 40, 20)
    y_vals = [i + 10 for i in x_vals]
    y2_vals = x_vals * 2
    y3_vals = x_vals ** 2
    
    ig.set_xlabel('x')
    ig.set_ylabel('y')
    ig.set_title('square')
    
    ig.plot(x_vals, y_vals, label='square root')
    ig.plot(x_vals, y2_vals, label='cube')
    ig.plot(x_vals, y3_vals, label='four')
    
    ig.set_legend_config('upper center')

    #ig.show()
    fig = ig.fig()
    ig.show()
    ig.save('t2')

    # caso 3:
    x_vals = ['val1', 'val2', 'val1', 'val1']
    y_vals = np.linspace(0, len(x_vals), 1)
    
    ig.set_xlabel('x values')
    ig.set_ylabel('y values')
    ig.set_title('values')
    
    ig.hist(x_vals)
    #ig.show()
    fig = ig.fig()
    ig.show()
    ig.save('t3')


    # caso 4:
    x_vals = ['val1', 'val2', 'val1', 'val1']
    labels = ['val1', 'val2']
    vals = [x_vals.count('val1'), x_vals.count('val2')]
    explode = [0.06, 0.06]
    
    ig.pie(vals, labels, explode)
    #ig.show()
    fig = ig.fig()
    ig.show()
    ig.save('t4')
    
    ig.__exit__()