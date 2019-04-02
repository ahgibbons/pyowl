# -*- coding: utf-8 -*-
"""
Created on Mon Apr  1 10:53:10 2019

@author: easan
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import pytz
import os

import json

import classes

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

MATCH_STATUS_CONCLUDED = "CONCLUDED"
MATCH_STATUS_PENDING = "PENDING"


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
        
def finished_matches(mcontent):
    return [m for m in mcontent if m['status']==MATCH_STATUS_CONCLUDED]
        
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
            
            
owl_data = load_from_disc()
team_dict = {}

for t in owl_data['ranking']['content']:
    t_id = t['competitor']['id']
    for team in owl_data['teams']['competitors']:
        if team['competitor']['id']==t_id:
            tjson = team['competitor']
    team_dict[t['competitor']['id']] = classes.Team(tjson,t)
    
matches_list = [classes.Match(m,team_dict) for m in finished_matches(owl_data['matches']['content'])]
matches_list.sort(key = lambda k: k.startTimeStamp)