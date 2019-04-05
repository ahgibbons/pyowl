# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""


import urllib
import posixpath
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import pytz
import os
import matplotlib.patches as patches
from PIL import Image

import OWLData
import classes
import Render
import Elo

from sklearn.neural_network import MLPClassifier

MATCH_STATUS_CONCLUDED = "CONCLUDED"
MATCH_STATUS_PENDING = "PENDING"


owl_divisions = {79 : 'ATL', 80 : 'PAC'}

map_type = ["KOTH Elo", "Hybrid Elo", "2CP Elo", "Escort Elo"]


owl_game_data = OWLData.owl_data   

owl_ranking = owl_game_data['ranking']
owl_matches = owl_game_data['matches']
owl_standings = owl_game_data['standings']
owl_teams = owl_game_data['teams']

cur_ranking = [a['competitor']['abbreviatedName'] for a in owl_ranking['content']]

match_content = owl_matches['content']
match_content.sort(key=lambda x: x['startDate'])
ranking_content = owl_ranking['content']  

team_dict = dict([(a['competitor']['abbreviatedName'],a['competitor']['id'])
    for a in owl_teams['competitors']])
    
def match_timestamp(match):
    return match['actualStartDate']


def match_plt_dates(matches):
    return [pltdate.date2num(datetime.fromtimestamp(i['actualStartDate']/1000,
        pytz.timezone("US/Pacific"))) for i in finished_matches(matches)]


def list_rankings():
    content = owl_ranking['content']
    team_id = [a['competitor']['id'] for a in content]
    teams = [a['competitor']['name'] for a in content]
    placement = [a['placement'] for a in content]
    gamewins = [a['records'][0]['gameWin'] for a in content]
    matchwins = [a['records'][0]['matchWin'] for a in content]
    return zip(team_id,teams, placement, matchwins, gamewins)

def gen_table():
    df = pd.DataFrame(list(list_rankings()), columns=['ID','Name', 'Placement', 'Match Wins', 'Map Wins'])
    return df



def match_result(match):
    A = match['competitors'][0]
    B = match['competitors'][1]
    
    print("{:s}:{:d} v {:s}:{:d}".format(A['name'], A['id'],
              B['name'], B['id']))
    
    scores = match['scores']
    A_score = scores[0]['value']
    B_score = scores[1]['value']
    
    if A_score > B_score:
        return 1
    else:
        return 0
    
def game_result(game):
    pass


    


def team_matches(team_id, match_list):
    matches = []
    for match in match_list:
        if match['competitors'][0]['id']==team_id:
            matches.append(match['id'])
        elif match['competitors'][1]['id']==team_id:
            matches.append(match['id'])
    return matches

def team_matches_full(team_id, match_list):
    matches = []
    for match in match_list:
        if match['competitors'][0]['id']==team_id:
            matches.append(match['id'])
        elif match['competitors'][1]['id']==team_id:
            matches.append(match)
    return matches


def get_match_data(match_id):
    match_path = os.path.join(owl_match_dir,str(match_id))
    games = []
    for i in os.listdir(match_path):
        with open(os.path.join(match_path, i)) as f:
            text = f.read()
        game_data = json.loads(text)
        games.append(game_data)
    return games



def team_compare(teamA, teamB):
    id_A = team_dict[teamA]
    id_B = team_dict[teamB]
    



def plot_team_elo(elo_track, team_name):
    plt.plot(elo_track[team_name]["Match Elo"],"--o", label="Total(Match)")
    plt.plot(elo_track[team_name]["Map Elo"],"--o", label="Total(Map)")
    plt.plot(elo_track[team_name]["KOTH Elo"],"-o", label="KOTH")
    plt.plot(elo_track[team_name]["Hybrid Elo"],"-o", label="Hybrid")
    plt.plot(elo_track[team_name]["2CP Elo"],"-o", label="2CP")
    plt.plot(elo_track[team_name]["Escort Elo"],"-o", label="Escort")
    plt.legend()
    plt.tight_layout()
    
    
def plot_elo_track(elo_track):
    ax1 = plt.subplot(231)
    ax2 = plt.subplot(232)
    ax3 = plt.subplot(233)
    ax4 = plt.subplot(234)
    ax5 = plt.subplot(235)
    ax6 = plt.subplot(236)
    
    lines = []
    
    for k in elo_track.keys():
        lines.append(ax1.plot(elo_track[k]["Map Elo"], label=k))
        ax2.plot(elo_track[k]["Map Elo(2)"], label=k)
        ax3.plot(elo_track[k]["KOTH Elo"], label=k)
        ax4.plot(elo_track[k]["Hybrid Elo"], label=k)
        ax5.plot(elo_track[k]["2CP Elo"], label=k)
        ax6.plot(elo_track[k]["Escort Elo"], label=k)
        
    ax1.set_title("Match Elo")
    ax2.set_title("Map Elo")
    ax3.set_title("KOTH Elo")
    ax4.set_title("Hybrid Elo")
    ax5.set_title("2CP Elo")
    ax6.set_title("Escort Elo")
    
    plt.figlegend(lines, labels=elo_track.keys(),prop={'size':'x-small'},ncol=2)
    
    
def team_result_summary(team_abbrev):
    team_id = team_dict[team_abbrev]
    
def plot_elo(elo_table, 
             elos=["Match Elo", "Map Elo", "KOTH Elo",
                   "Hybrid Elo", "2CP Elo", "Escort Elo"], ax=None):
    if ax:
        ax = elo_table.plot.bar(x="Abbrev",
                y=elos,ax=ax)
    else:
        ax = elo_table.plot.bar(x="Abbrev",
                y=elos)
    plt.ylim(1350,1700)
    #plt.xlabel("Team")
    plt.ylabel("Elo Rating")
    
    plt.legend(frameon=False)
    
    plt.tight_layout()
    return ax
    
def finalized_elo_plot(elo_table):
    ax1 = plt.subplot(211)
    ax1.set_title("Overall Elo Rating")
    plot_elo(elo_table, elos=["Match Elo", "Map Elo", "Map Elo(2)"],ax=ax1)
    ax2 = plt.subplot(212)
    ax2.set_title("Map Type Elo")
    plot_elo(elo_table, elos=["KOTH Elo",
                   "Hybrid Elo", "2CP Elo", "Escort Elo"],ax=ax2)
    ax2.set_ylim(1350,1650)
    ax1.set_xlabel('')
    ax2.set_xlabel('')
    plt.tight_layout()
    
def plot_elo_date(elo,elo_type='Match Elo'):
    elo_track_time  = elo.elo_track_time
    
    
    fig = plt.figure()
    
    for t in team_dict.keys():
        teamObj = OWLData.team_dict[team_dict[t]]
        elo_time = elo_track_time[t][elo_type]
        d,e = zip(*elo_time)
        #plt.step(d,e,'-o',label=t,where='post')
        plt.plot(d,e,'-o',label=t,color="#"+teamObj.primaryColor)
        plt.annotate(t,elo_time[-1])
    
    
