import json
from numbers_parser import Document
import pandas as pd
from datetime import date
import pdb
from sheet import Sheet
from game import Game




class Team():
    def __init__(self,name,roster,home,pitcher):
        path = "template.numbers"
        self.name = name
        self.roster = roster
        self.home = home
        self.atBat = 0 
        self.pitcher = pitcher
        self.stats = Sheet(path)
        self.stats.initPitcher(name)
        self.stats.addPitcher(pitcher, True)
        self.stats.setRoster(roster,name)

    def changePitcher(self,pitcher1):
        self.pitcher = pitcher1
        self.stats.addPitcher(pitcher1)

class BaseRunner():
    def __init__(self,name,pitcher): 
        self.name = name
        self.pitcher = pitcher

def getTeams():
    league = ["Conrad", "Charlie", "Elliot", "Noah", "Michael"] 
    retry = True
    while retry: 
            while True:
                team1 = input("Enter the first person: ")
                if team1 in league: 
                    break
                else: 
                    print("Please enter a valid team")
            
            while True:
                team2 = input("Enter the second person: ")
                if team2 == team1: 
                    print("Second team can not be the same as the first")
                elif team2 in league: 
                    break
                else: 
                    print("Please enter a valid team")
            print(f'Game is {team1} vs {team2}')
            retry = input("If these teams are incorrect press r if correct click anything") == "r"
    return (team1,team2)


def readJson(file):
    with open(file) as f: 
        teams = json.load(f)
    return teams

def setLineups(team1_name, team2_name, roster1,roster2): 
    print(f"{team1_name} please set ur lineup")
    team1 = getHitters(roster1)
    print(f"{team2_name} please set ur lineup")
    team2 = getHitters(roster2)
    
    print(f"{team1_name} please choose ur pitcher")
    pitch1 = getPitcher(roster1)

    print(f"{team2_name} please choose ur pitcher")
    pitch2 = getPitcher(roster2)

    home1, home2 = getHome(team1_name,team2_name)
    t1 = Team(team1_name,team1,home1,pitch1)
    t2 = Team(team2_name,team2,home2,pitch2)
    return (t1 , t2) if home1 else (t2,t1)

def getPitcher(roster): 
    while True: 
        pitch = input("Who is pitching: ")
        if pitch in roster: 
            print(f"{pitch} is pitching: ")
            break
        else: 
            print("Please print a valid pitcher")
    return pitch



def getHitters(roster1): 
    inp = ""
    while inp != "y":
        inp = ""
        lp = []
        print("Please write your lineup 1-9 by clicking the hotkey corresponding to each player")
        print("Here is your roster:")
        player_to_key = {player : str(i) for i,player in enumerate(roster1)}
        key_to_player = {player_to_key[player] : player for player in player_to_key }

        print("Player : Hotkey")
        for play in roster1: 
            print(f"{play} : {player_to_key[play]}")
        
        print("")
        print("If a mistake was made, press u to remove last entry")
        i = 0 
        while i < 9: 
            hit = input(f"{i + 1}.")
            if hit not in key_to_player and hit != "u": 
                print("Please enter a valid hitter")
                break
            elif hit == 'u':
                lp = lp[:-1]
                i -=2
                if i < 0: i=-1
            elif key_to_player[hit] in lp: 
                print(f"{key_to_player[hit]} is already playing!")
                i -=1

            elif key_to_player[hit] in roster1: 
                print(key_to_player[hit])
                lp.append(key_to_player[hit])
            
            i += 1 
        print("Lineup entered : ")
        for j, player in enumerate(lp): 
            print(f"{j+1}. {player}")
        while inp != 'y' and inp !='n':
            inp = input("Is lineup correct? (y/n)")
    return lp


def getInnings():
    while True: 
        ings = input("How many innngs? ")
        try:
            ings = int(ings)  # Convert input to a float
            if ings >=0 and ings < 10: 
                     break
            else: 
                print(f"Please enter a non-negative integer less than 10")
        except ValueError:
                print("Invalid input. Please enter a numerical value.")
    return ings

def getStadium(): 
    stad = input("What stadium? ")
    return stad

def getTime():
    while True: 
        time = input("Night or Day? ")
        if time == "Night" or time == "Day": 
            return time
        else: 
            print("Please enter either Night or Day")


def getHome(n1,n2):
    while True: 
        home = input("Who is the home team today?")
        if home != n1 and home != n2: 
            print(f"Please enter either {n1} or {n2}")
        else: 
            print(f"{home} is the home team.")
            break
    return (n1 == home, n2 == home)

def export(team1,team2,game):
     postProcessing(team1,team2,game)
     hitting = pd.concat([team1.stats.hitting,team2.stats.hitting])
     pitching = pd.concat([team1.stats.pitching,team2.stats.pitching])
     title = str(date.today()) + team1.name + " vs " + team2.name + " " + game.stadium + " at " + game.time + ".xlsx"
     with pd.ExcelWriter(title, engine='xlsxwriter') as writer:
            # Write each dataframe to a separate worksheet
            hitting.to_excel(writer, sheet_name='Hitting', index=True)
            pitching.to_excel(writer, sheet_name='Pitching', index=True)
            game.box_score.to_excel(writer, sheet_name="Box Score", index=True)

def postProcessing(team1,team2,game): 
    team1.stats.outsToIP()
    team2.stats.outsToIP()
    game.wAndl()
    game.finalBox(team1,team2)
    
def initGame(): 
    ings = getInnings()
    stadium = getStadium()
    time = getTime()
    return (ings,stadium,time)
    


def main(): 
    teams_file = "teams.json"
    teams = readJson(teams_file)

    print("==================")
    print("| Slugger's Stats |")
    print("==================\n")
   

    print("Who is playing?")
    team1_name, team2_name = getTeams()
    print(f"Game is set {team1_name} vs {team2_name}")
    
    print("==================")
    
    print("Time to set lineups")
    roster1 = teams[team1_name]
    roster2 = teams[team2_name]
    home, away = setLineups(team1_name,team2_name,roster1,roster2)

    innings, stadium, time = initGame()
    game = Game(innings,home,away, stadium, time)
    
    
    print("Starting the game!")
    print("==================\n\n")
    game.play()


    export(home,away,game)




def temp():
    #temp_path = "template.numbers"
    roster = readJson("teams.json")['Conrad']
    roster1 = readJson("teams.json")["Michael"]
    team1 = Team("Conrad", roster, True,"Bowser Jr.")
    team2 = Team("Michael", roster1, False, "Wario")
    game = Game(2,team1,team2,"Mario", "Night")
    game.play()

    export(team1,team2,game)

if __name__ == "__main__":
    main()
    #temp()