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
import matplotlib.patches as patches
import pandas as pd

import OWLData

TEAM_NUM = 20

id_index = dict(zip(OWLData.team_dict.keys(),range(20)))
team_index = {}
for n,i in OWLData.team_id.items():
    team_index[n] = id_index[i]
    
class BradleyTerry:
    def __init__(self,matches,iterations):
        p = P_vector()
        wins = make_map_win_records(matches)
        for _ in range(iterations):
            p = update_P(p,wins)
        
        self.p_list = p
        self.p = dict(zip(team_index.keys(),p))
    
    def verses(self,team1,team2):
        p1 = self.p[team1]
        p2 = self.p[team2]
        
        prob1 = p1/(p1+p2)
        prob2 = p2/(p1+p2)
        
        print("{:s}: {:.1f} %, {:s}: {:.1f} %".format(team1,100*prob1,team2,100*prob2))
        
        return (prob1, prob2)
    
    def predict_series(self,team1,team2):
        p1 = self.p[team1]
        p2 = self.p[team2]
        prob1 = p1/(p1+p2)
        prob2 = p2/(p1+p2)
        
        p1_win = prob1**4 + 4*(prob1**3)*prob2 + 6*(prob1**3)*(prob2**2)
        p2_win = prob2**4 + 4*(prob2**3)*prob1 + 6*(prob2**3)*(prob1**2)
        
        print("{:s}: {:.1f} %, {:s}: {:.1f} %".format(team1,100*p1_win,team2,100*p2_win))
        
        return (p1_win, p2_win)
    
    def ranking(self):
        bt_list = list(self.p.items())
        bt_list.sort(key= lambda a: a[1], reverse=True)
        return [b[0] for b in bt_list]
        
    def plot_rank(self):
        teams = list(OWLData.team_dict.values())
        teams.sort(key= lambda t: t.placement)
        bt_rank = self.ranking()
        owl_rank = [t.abbreviatedName for t in teams]
        
        rank_compare = [(owl_rank.index(a)+1, bt_rank.index(a)+1) for a in owl_rank]
        
        xs,ys = zip(*rank_compare)
        ax = plt.subplot(111)
        t1 = patches.Polygon([(1,1),(20,20),(1,20)],facecolor='#ffbbbb')
        t2 = patches.Polygon([(1,1),(20,20),(20,1)],facecolor='#bbffbb')
        #ax.add_patch(t1)
        #ax.add_patch(t2)
        plt.scatter(xs,ys)
        plt.xlim(21,0)
        plt.ylim(21,0)


def P_vector():
    P = np.full(TEAM_NUM,1/TEAM_NUM,dtype='float')
    return P

def L(P,w):
    ans = 0
    for i in range(TEAM_NUM):
        for j in range(TEAM_NUM):
           a = w[i][j]*np.log(P[i]) - w[i][j]*np.log(P[i]+P[j])
           ans += a
           
    return ans

def update_P(P,w):
    W = w.sum(axis=1)
    p1 = np.zeros(TEAM_NUM, dtype='float')
    for i in range(TEAM_NUM):
        Wi = W[i]
        u = 0
        for j in range(TEAM_NUM):
            if j != i:
                a = (w[i][j] + w[j][i])/(P[i] + P[j])
                u += a
        p1[i] = Wi/u
    
    p_sum = p1.sum()
    return p1/p_sum
        
        

def prob(p1,p2):
    return (p1 / (p1+p2))

def make_map_win_records(matchlist):
    win_records = np.zeros((20,20))
    for m in matchlist:
        t0 = m['competitors'][0]
        t1 = m['competitors'][1]
        
        i0 = id_index[t0['id']]
        i1 = id_index[t1['id']]
        
        s0 = m['scores'][0]['value']
        s1 = m['scores'][1]['value']
        
        
        win_records[i0][i1] += s0
        win_records[i1][i0] += s1
        
    return win_records
        


def make_match_win_records(matchlist):
    win_records = np.zeros((20,20))
    
    for m in matchlist:
        t0 = m['competitors'][0]
        t1 = m['competitors'][1]
        
        i0 = id_index[t0['id']]
        i1 = id_index[t1['id']]
        
        s0 = m['scores'][0]['value']
        s1 = m['scores'][1]['value']
        
        r0,r1 = (1,0) if s0>s1 else (0,1)
        
        win_records[i0][i1] += r0
        win_records[i1][i0] += r1
        
    return win_records

def create_BT_plot():
    pass