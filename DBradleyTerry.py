# -*- coding: utf-8 -*-
"""
Created on Tue Mar 19 11:22:30 2019

@author: easan
"""

"""
Dynamic Bradley-Terry
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

class Player:
    def __init__(self, id_num):
        self.ID = id_num
    
    def elo(self, t):
        pass
    
    def gamma(self,t):
        return np.power(self.elo()/400)
    
    def natural_rating(self,t):
        np.log(10)*self.elo()/400
        
    
def BT_probability(pi,pj,t):
    return pi.gamma(t) / (pi.gamma(t) + pj.gamma(t))
    