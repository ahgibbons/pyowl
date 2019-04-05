# -*- coding: utf-8 -*-
"""
Created on Mon Apr  1 11:02:30 2019

@author: easan
"""
from datetime import datetime, timedelta
import pytz

owl_divisions = {79 : 'ATL', 80 : 'PAC'}

class Team:
    def __init__(self,tjson,rjson):
        self.id = tjson['id']
        self.name = tjson['name']
        self.abbreviatedName = tjson['abbreviatedName']
        self.division = owl_divisions[tjson['owl_division']]
        self.division_id = tjson['owl_division']
        self.placement = rjson['placement']
        self.matchwin = rjson['records'][0]['matchWin']
        self.matchloss = rjson['records'][0]['matchLoss']
        self.gamewin = rjson['records'][0]['gameWin']
        self.gameloss = rjson['records'][0]['gameLoss']
        self.primaryColor = tjson['primaryColor']
        self.secondaryColor = tjson['secondaryColor']
        self.placement = rjson['placement']
        
class Match:
    def __init__(self,mjson,team_dict):
        self.id = mjson['id']
        self.team_ids = [t['id'] for t in mjson['competitors']]
        self.teams = [team_dict[i] for i in self.team_ids]
        self.scores = [s['value'] for s in mjson['scores']]
        self.state = mjson['state']
        self.startTimeStamp = mjson['startDate']
        self.startTime = datetime.fromtimestamp(mjson['actualStartDate']/1000,
                                    pytz.timezone("US/Pacific"))
        
        if self.scores[0] > self.scores[1]:
            self.winner = self.teams[0]
        else:
            self.winner = self.teams[1]