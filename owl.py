# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import json
import urllib
import posixpath
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import pytz
import os
import matplotlib.patches as patches
from PIL import Image

from sklearn.neural_network import MLPClassifier

MATCH_STATUS_CONCLUDED = "CONCLUDED"
MATCH_STATUS_PENDING = "PENDING"


owl_data_dir = "data"
owl_match_dir = os.path.join("data","matches")
owl_logo_svg_dir = os.path.join("data","logos_svg")
owl_logo_png_dir = os.path.join("data","logos_svg")

owl_url_root = "https://api.overwatchleague.com/"
owl_extensions = ["ranking", "standings", "matches", "teams"]
owl_url_ranking = "https://api.overwatchleague.com/ranking"
owl_url_standings = "https://api.overwatchleague.com/standings"
owl_url_matches = "https://api.overwatchleague.com/matches"
owl_url_match_stat_test = "https://api.overwatchleague.com/stats/matches/21211/maps/1"
owl_url_match_stat = "https://api.overwatchleague.com/stats/matches/"
owl_url_teams = "https://api.overwatchleague.com/teams"
owl_url_players = "https://api.overwatchleague.com/teams"
owl_url_stat_players = "https://api.overwatchleague.com/stats/players"

update_url_list = [owl_url_ranking,owl_url_standings, owl_url_matches,
                   owl_url_teams,owl_url_players, owl_url_stat_players]

owl_divisions = {79 : 'ATL', 80 : 'PAC'}

class Team:
    def __init__(self,tjson,rjson):
        self.id = tjson['id']
        self.name = tjson['name']
        self.abbreviatedName = tjson['abbreviatedName']
        self.division = owl_divisions[tjson['owl_division']]
        self.division_id = tjson['owl_division']
        self.placement = rjson['placement']
        self.matchwin = rjson['records']['matchWin']
        self.matchloss = rjson['records']['matchLoss']
        self.gamewin = rjson['records']['gameWin']
        self.gameloss = rjson['records']['gameLoss']
        self.primaryColor = tjson['primaryColor']
        self.secondaryColor = tjson['secondaryColor']
        
def draw_logos():
    fig = plt.figure(figsize=(5,5))
        

map_type = ["KOTH Elo", "Hybrid Elo", "2CP Elo", "Escort Elo"]
elo_K_factor =  50

def load_from_website():
    owl_ranking_text = urllib.request.urlopen(owl_url_ranking).read()
    owl_matches_text = urllib.request.urlopen(owl_url_matches).read()
    owl_standings_text = urllib.request.urlopen(owl_url_standings).read()
    owl_teams_text = urllib.request.urlopen(owl_url_teams).read()
    
    owl_ranking = json.loads(owl_ranking_text)
    owl_matches = json.loads(owl_matches_text)
    owl_standings = json.loads(owl_standings_text)
    owl_teams = json.loads(owl_teams_text)
    

    return {'ranking' : owl_ranking, 'matches' : owl_matches, 
            'standings' : owl_standings, 'teams' : owl_teams}

def load_from_disc(data_dir = owl_data_dir):
    with open(os.path.join(data_dir, 'matches.json'),'r') as f:
        owl_matches_text = f.read()

    with open(os.path.join(data_dir, 'ranking.json'),'r') as f:
        owl_ranking_text = f.read()

    with open(os.path.join(data_dir, 'standings.json'),'r') as f:
        owl_standings_text = f.read()
        
    with open(os.path.join(data_dir, 'teams.json'),'r') as f:
        owl_teams_text = f.read()
    
    owl_ranking = json.loads(owl_ranking_text)
    owl_matches = json.loads(owl_matches_text)
    owl_standings = json.loads(owl_standings_text)
    owl_teams = json.loads(owl_teams_text)

    return {'ranking' : owl_ranking, 'matches' : owl_matches, 
            'standings' : owl_standings, 'teams' : owl_teams}

owl_data = load_from_disc()    

owl_ranking = owl_data['ranking']
owl_matches = owl_data['matches']
owl_standings = owl_data['standings']
owl_teams = owl_data['teams']

match_content = owl_matches['content']
match_content.sort(key=lambda x: x['startDate'])
ranking_content = owl_ranking['content']  

team_dict = dict([(a['competitor']['abbreviatedName'],a['competitor']['id'])
    for a in owl_teams['competitors']])
    
    
    


def download_data():
    for url in owl_extensions:
        durl = urllib.parse.urljoin(owl_url_root, url)
        page_text = urllib.request.urlopen(durl).read()
        with open(os.path.join(owl_data_dir,url)+".json",'wb') as file:
            file.write(page_text)
        print("Downloaded "+url)
        
def download_logos_svg():
    for t in owl_teams['competitors']:
        img_data = urllib.request.urlopen(t['competitor']['icon']).read()
        name = t['competitor']['abbreviatedName']
        file_name = "{:s}.svg".format(name)
        with open(os.path.join(owl_logo_svg_dir, file_name),'wb') as f:
            f.write(img_data)
        print("Downloaded {:s} icon".format(name))
        
def download_logos_png():
    for t in owl_teams['competitors']:
        img_data = urllib.request.urlopen(t['competitor']['logo']).read()
        name = t['competitor']['abbreviatedName']
        file_name = "{:s}.png".format(name)
        with open(os.path.join(owl_logo_svg_dir, file_name),'wb') as f:
            f.write(img_data)
        print("Downloaded {:s} logo".format(name))
        
def download_match_data(matches):
    for match in matches:
        mid = match['id']
        ngames = len(match['games'])
        mdir = os.path.join(owl_match_dir,str(mid))
        if not os.path.isdir(mdir):
            os.mkdir(mdir)
        for i in range(1,ngames+1):
            durl = posixpath.join(owl_url_match_stat, str(mid), "maps", str(i))
            page_text = urllib.request.urlopen(durl).read()
            with open(os.path.join(mdir,str(i))+".json",'wb') as file:
                file.write(page_text)
            print("Downloaded {:d} {:d}".format(mid,i))
    
def match_timestamp(match):
    return match['actualStartDate']

def gen_elo_track(start_elo=1500):
    teams = [a['competitor']['name'] for a in ranking_content]
    team_id = [a['competitor']['id'] for a in ranking_content]
    elo_track = [{"Match Elo" : [start_elo], "Map Elo" : [start_elo],
                  "Map Elo(2)" : [start_elo], "KOTH Elo" : [start_elo],
                  "Hybrid Elo" : [start_elo], "2CP Elo" : [start_elo], "Escort Elo" : [start_elo]}
                for a in match_content]
    return dict(zip(teams,elo_track))

def match_plt_dates(matches):
    return [pltdate.date2num(datetime.fromtimestamp(i['actualStartDate']/1000,
        pytz.timezone("US/Pacific"))) for i in finished_matches(matches)]

def gen_begin_table():    
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

def finished_matches(mcontent):
    return [m for m in mcontent if m['status']==MATCH_STATUS_CONCLUDED]

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
    
def update_match(match, elo_table, elo_track):
    A = match['competitors'][0]
    B = match['competitors'][1]
    
    A_id = A['id']
    B_id = B['id']
    
    result = match_score(match)
    result2 = match_score2(match)
    
    RA = elo_table.loc[elo_table['ID'] == A_id, 'Match Elo'].values[0]
    RB = elo_table.loc[elo_table['ID'] == B_id, 'Match Elo'].values[0]
    RA_2, RB_2 = elo_update(RA,RB,result)
    
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
    
    RA_map = elo_table.loc[elo_table['ID'] == A_id, 'Map Elo'].values[0]
    RB_map = elo_table.loc[elo_table['ID'] == B_id, 'Map Elo'].values[0]
    
    for n,elo_type in enumerate(map_type):
        points_A, points_B = match['games'][n]['points']
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
        
        print("{:s} vs {:s};\t{:f} -> {:f}".format(A['abbreviatedName'],
                      B['abbreviatedName'], RA_map_old, RA_map))
        
    elo_table.loc[elo_table['ID']==A_id, "Map Elo"] = RA_map
    elo_table.loc[elo_table['ID']==B_id, "Map Elo"] = RB_map
    
    elo_track[A['name']]["Map Elo"].append(RA_map)
    elo_track[B['name']]["Map Elo"].append(RB_map)
    
    
    return elo_track

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

def calc_elo(match_list,elo_table,elo_track):
    for m in match_list:
        update_match(m, elo_table, elo_track)
        

def get_match_data(match_id):
    match_path = os.path.join(owl_match_dir,str(match_id))
    games = []
    for i in os.listdir(match_path):
        with open(os.path.join(match_path, i)) as f:
            text = f.read()
        game_data = json.loads(text)
        games.append(game_data)
    return games

def elo_expected(RA,RB):
    QA = 10**(RA/400)
    QB = 10**(RB/400)
    
    EA = QA/(QA+QB)
    EB = QB/(QA+QB)
    return (EA,EB)

def team_compare(teamA, teamB):
    id_A = team_dict[teamA]
    id_B = team_dict[teamB]
    

def elo_update(RA,RB,SA, K=elo_K_factor):
    """Update Elo of RA, RB. SA is 1 for A win, 0 for B win,
    0.5 for a draw"""
    
    SB = 1 - SA
    EA,EB = elo_expected(RA,RB)
    
    RA += K*(SA - EA)
    RB += K*(SB - EB)
    
    return (RA,RB)

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
