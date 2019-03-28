# -*- coding: utf-8 -*-
"""
Created on Tue Mar 19 11:20:43 2019

@author: easan
"""

def elo_expected(RA,RB):
    QA = 10**(RA/400)
    QB = 10**(RB/400)
    
    EA = QA/(QA+QB)
    EB = QB/(QA+QB)
    return (EA,EB)

def elo_update(RA,RB,SA, K=elo_K_factor):
    """Update Elo of RA, RB. SA is 1 for A win, 0 for B win,
    0.5 for a draw"""
    
    SB = 1 - SA
    EA,EB = elo_expected(RA,RB)
    
    RA += K*(SA - EA)
    RB += K*(SB - EB)