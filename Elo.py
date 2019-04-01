# -*- coding: utf-8 -*-
"""
Created on Tue Mar 19 11:20:43 2019

@author: easan
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta
import pytz

import OWLData

elo_K_factor =  50
map_type = ["KOTH Elo", "Hybrid Elo", "2CP Elo", "Escort Elo", "KOTH Elo",
            "Hybrid Elo", "Escort Elo", "KOTH Elo"]

start_time = datetime.fromtimestamp(1550102990.348, pytz.timezone("US/Pacific"))

class OWL_Elo:
    def __init__(self,kfactor=elo_K_factor):
        self.elo_table = gen_begin_table()
        self.elo_track = gen_elo_track() 
        self.elo_track_time = gen_elo_track_time()
        self.k_factor = elo_K_factor
        
    def calc_elo(self, match_list):
        errors = [self.update_match(m) for m in match_list]
        return errors
        

        
    def update_match(self,match):
        elo_table = self.elo_table
        elo_track = self.elo_track
        elo_track_time = self.elo_track_time
        
        match_time = datetime.fromtimestamp(match['actualStartDate']/1000,pytz.timezone("US/Pacific"))
        
        A = match['competitors'][0]
        B = match['competitors'][1]
    
        A_id = A['id']
        B_id = B['id']
    
        result = match_score(match)
        result2 = match_score2(match)
        
        RA = elo_table.loc[elo_table['ID'] == A_id, 'Match Elo'].values[0]
        RB = elo_table.loc[elo_table['ID'] == B_id, 'Match Elo'].values[0]
        RA_2, RB_2 = elo_update(RA,RB,result)
        
        prediction_error = predict_error(RA, RB, result)

        
        elo_table.loc[elo_table['ID']==A_id, 'Match Elo'] = RA_2
        elo_table.loc[elo_table['ID']==B_id, 'Match Elo'] = RB_2
        
        RA_m2 = elo_table.loc[elo_table['ID'] == A_id, 'Map Elo(2)'].values[0]
        RB_m2 = elo_table.loc[elo_table['ID'] == B_id, 'Map Elo(2)'].values[0]
        RA_m2_2, RB_m2_2 = elo_update(RA_m2,RB_m2,result2)
        
        elo_table.loc[elo_table['ID']==A_id, 'Map Elo(2)'] = RA_m2_2
        elo_table.loc[elo_table['ID']==B_id, 'Map Elo(2)'] = RB_m2_2
    
        if result:
            elo_table.loc[elo_table['ID']==A_id, 'Wins'] += 1
        else:
            elo_table.loc[elo_table['ID']==B_id, 'Wins'] += 1

        elo_track[A['name']]["Match Elo"].append(RA_2)
        elo_track[B['name']]["Match Elo"].append(RB_2)
        
        elo_track[A['name']]["Map Elo(2)"].append(RA_m2_2)
        elo_track[B['name']]["Map Elo(2)"].append(RB_m2_2)
        
        elo_track_time[A['abbreviatedName']]["Match Elo"].append((match_time,RA_2))
        elo_track_time[B['abbreviatedName']]["Match Elo"].append((match_time,RB_2))
        
        elo_track_time[A['abbreviatedName']]["Map Elo(2)"].append((match_time,RA_m2_2))
        elo_track_time[B['abbreviatedName']]["Map Elo(2)"].append((match_time,RB_m2_2))
        
        RA_map = elo_table.loc[elo_table['ID'] == A_id, 'Map Elo'].values[0]
        RB_map = elo_table.loc[elo_table['ID'] == B_id, 'Map Elo'].values[0]
    
        for g,elo_type in zip(match['games'],map_type):
            points_A, points_B = g['points']
            if points_A > points_B:
                result = 1
            elif points_A < points_B:
                result = 0
            else:
                result = 0.5
        
            RA_map_old = RA_map
            RB_map_old = RB_map
        
            RA = elo_table.loc[elo_table['ID'] == A_id, elo_type].values[0]
            RB = elo_table.loc[elo_table['ID'] == B_id, elo_type].values[0]
            RA_2, RB_2 = elo_update(RA,RB,result)
            RA_map, RB_map = elo_update(RA_map, RB_map, result)
        
    
            elo_table.loc[elo_table['ID']==A_id, elo_type] = RA_2
            elo_table.loc[elo_table['ID']==B_id, elo_type] = RB_2

            elo_track[A['name']][elo_type].append(RA_2)
            elo_track[B['name']][elo_type].append(RB_2)
            
            elo_track_time[A['abbreviatedName']][elo_type].append((match_time,RA_2))
            elo_track_time[B['abbreviatedName']][elo_type].append((match_time,RB_2))
        
            print("{:s} vs {:s};\t{:f} -> {:f}".format(A['abbreviatedName'],
                      B['abbreviatedName'], RA_map_old, RA_map))
        
        elo_table.loc[elo_table['ID']==A_id, "Map Elo"] = RA_map
        elo_table.loc[elo_table['ID']==B_id, "Map Elo"] = RB_map
    
        elo_track[A['name']]["Map Elo"].append(RA_map)
        elo_track[B['name']]["Map Elo"].append(RB_map)
        
        elo_track_time[A['abbreviatedName']]["Map Elo"].append((match_time,RA_map))
        elo_track_time[B['abbreviatedName']]["Map Elo"].append((match_time,RB_map))
        
        return prediction_error
    
    
def gen_begin_table():    
    ranking_content = OWLData.owl_data['ranking']['content']
    teams = [a['competitor']['name'] for a in ranking_content]
    team_id = [a['competitor']['id'] for a in ranking_content]
    team_abbrev = [a['competitor']['abbreviatedName'] for a in ranking_content]
    team_placement = [a['placement'] for a in ranking_content]
    def_elo_match = [1500 for a in teams]
    def_elo_map = [1500 for a in teams]
    def_elo_map2 = [1500 for a in teams]
    def_elo_koth = [1500 for a in teams]
    def_elo_hybrid = [1500 for a in teams]
    def_elo_2CP = [1500 for a in teams]
    def_elo_escort = [1500 for a in teams]
    def_wins = [0 for a in teams]
    df = pd.DataFrame(list(zip(team_id,teams,team_abbrev, team_placement,
                               def_wins,def_elo_match, def_elo_map,
                               def_elo_map2,
                               def_elo_koth, def_elo_hybrid, def_elo_2CP,
                               def_elo_escort)),
             columns=['ID','Name', 'Abbrev', "Placement", "Wins", "Match Elo", "Map Elo",
                      "Map Elo(2)", "KOTH Elo",
                      "Hybrid Elo", "2CP Elo", "Escort Elo"])
    
    return df

def gen_elo_track(start_elo=1500):
    ranking_content = OWLData.owl_data['ranking']['content']
    match_content = OWLData.owl_data['matches']['content']
    teams = [a['competitor']['name'] for a in ranking_content]
    team_id = [a['competitor']['id'] for a in ranking_content]
    elo_track = [{"Match Elo" : [start_elo], "Map Elo" : [start_elo],
                  "Map Elo(2)" : [start_elo], "KOTH Elo" : [start_elo],
                  "Hybrid Elo" : [start_elo], "2CP Elo" : [start_elo], "Escort Elo" : [start_elo]}
                for a in match_content]
    return dict(zip(teams,elo_track))

def gen_elo_track_time(start_elo=1500, start_time=start_time):
    ranking_content = OWLData.owl_data['ranking']['content']
    match_content = OWLData.owl_data['matches']['content']
    teams = [a['competitor']['abbreviatedName'] for a in ranking_content]
    team_id = [a['competitor']['id'] for a in ranking_content]
    elo_track = [{"Match Elo" : [(start_time,start_elo)], "Map Elo" : [(start_time,start_elo)],
                  "Map Elo(2)" : [(start_time,start_elo)], "KOTH Elo" : [(start_time,start_elo)],
                  "Hybrid Elo" : [(start_time,start_elo)], 
                  "2CP Elo" : [(start_time,start_elo)], "Escort Elo" : [(start_time,start_elo)]}
                for a in match_content]
    return dict(zip(teams,elo_track))

def match_score(match):
    scores = match['scores']
    A_score = scores[0]['value']
    B_score = scores[1]['value']
    if A_score > B_score:
        result = 1
    else:
        result = 0
        
    return result

def match_score2(match):
    scores = match['scores']
    A_score = scores[0]['value']
    B_score = scores[1]['value']
    result = (A_score - B_score)/8+0.5
        
    return result

def elo_update(RA,RB,SA, K=elo_K_factor):
    """Update Elo of RA, RB. SA is 1 for A win, 0 for B win,
    0.5 for a draw"""
    
    SB = 1 - SA
    EA,EB = elo_expected(RA,RB)
    
    RA += K*(SA - EA)
    RB += K*(SB - EB)
    
    return (RA,RB)

def predict_error(RA,RB,SA):
    """Prediction Error. SA is 1 for A win, 0 for B win,
    0.5 for a draw"""
    
    SB = 1 - SA
    EA,EB = elo_expected(RA,RB)
    
    err = abs(EA - SA)
    
    return err
    
def rightwrong(e):
    if e<0.5:
        return 1
    elif e>0.5:
        return -1
    else:
        return 0

def elo_expected(RA,RB):
    QA = 10**(RA/400)
    QB = 10**(RB/400)
    
    EA = QA/(QA+QB)
    EB = QB/(QA+QB)
    return (EA,EB)