import pandas as pd 
from functools import partial


class Game(): 
    def __init__(self,innings,home,away,stadium,time): 
        self.innings = innings * 2
        self.current_inning = 0
        self.home = home
        self.away = away
        self.home_score = 0
        self.away_score = 0 
        self.stadium = stadium
        self.time = time
        self.pitch_win = None
        self.pitch_loss = None
        self.box_score = self.initBox(home,away,innings)
        

    def initBox(self,home,away,innings): 
        index = pd.Index([away.name,home.name], name='Teams')
        df = pd.DataFrame(index=index, columns=range(1,innings+1))
        df = df.fillna(0)
        return df
    
    def addBox(self): 
        ing  = self.current_inning //2  + 1
        self.box_score[ing] = [0,0]


    
    def gameOver(self):
        if self.current_inning >= self.innings and self.current_inning %2 == 0 and self.away_score != self.home_score:
            print ("Game is over!") 
            return True
        if self.current_inning + 1 == self.innings and self.home_score > self.away_score: 
            self.box_score.loc[self.home.name,self.innings // 2] = "x"
            print ("Game is over!") 
            return True
        return False
    
    def simhalfing(self,batting,pitching):
        outs = 0 
        bases = []
        r = 0 
        buffer = []
        #Bases, Outs, Runs 
        game_state = [[],0,0]
        while outs < 3: 
            atBat = batting.roster[batting.atBat]
            print(f"{pitching.pitcher} is pitching")
            print(f"{atBat} is batting")
            change = input("To change pitcher press c: ")
            while change == "c": 
                pitching.pitcher = self.getPitcher(pitching.roster)
                pitching.stats.addPitcher(pitching.pitcher,False)
                print(f"{atBat} is batting")
                change = input("To change pitcher press c: ")
                print(f"{pitching.pitcher} is pitching")
                print(f"{atBat} is batting")

            result = self.getAtBatResult()
            if result == "u": 
                buffer = []
                outs = game_state[1]
                bases = game_state[0]
                r = game_state[2]
                batting.atBat -= 1
                if batting.atBat <0: batting.atBat = 8 
                continue 
            else: 
                for call in buffer: 
                    call()
                game_state = [bases.copy(),outs,r]
                
            if result != "o" and result != "r" and result != "f": 
                buffer.append(partial(pitching.stats.recordPitcherEvent,result,1,pitching.pitcher) )
                    #pitching.stats.recordPitcherEvent(result,1,pitching.pitcher))
            if result != "o" and result != "f": 
                buffer.append(partial(batting.stats.recordBatterEvent,result,1,atBat))
                
                #batting.stats.recordBatterEvent(result,1,atBat)
            outso = outs
            bases, o, runs = self.updateBases(bases,result,atBat,batting,outs,buffer)   
            outs = o 
            buffer.append(partial(pitching.stats.recordPitcherEvent,"IP",o-outso,pitching.pitcher))
            #pitching.stats.recordPitcherEvent("IP",o-outso,pitching.pitcher)
            print(f"Bases : {bases}, outs : {o}")
            if result != "w":  
                buffer.append(partial(batting.stats.recordBatterEvent,"AB",1,atBat))
                #batting.stats.recordBatterEvent("AB",1,atBat)
            if o -1 == outs and runs:
               buffer.append(batting.stats.recordBatterEvent,"AB",-1,atBat)
               #batting.stats.recordBatterEvent("AB",-1,atBat)
            r += runs
            if runs: 
                buffer.append(partial(pitching.stats.recordPitcherEvent,"R",runs,pitching.pitcher))
                #pitching.stats.recordPitcherEvent("R", runs, pitching.pitcher)
                buffer.append(partial(self.updateScore,runs,batting))
                if self.current_inning >= self.innings-1 and self.home_score > self.away_score and self.current_inning % 2 == 1:
                    self.updateBoxScore(r,batting)
                    print("Walk off!")
                    return 1  

            batting.atBat = (batting.atBat + 1) % 9
            if outs >= 3: 
                inp = input("Inning is over, if a mistake was made press m to go back\nelse press anything")
                if inp == "m":
                    buffer = []
                    outs = game_state[1]
                    bases = game_state[0]
                    r = game_state[2]
                    batting.atBat -= 1
                    if batting.atBat <0: batting.atBat = 8 
                else: 
                    for call in buffer: 
                        call()
        if r: 
            #pdb.set_trace()
            self.updateBoxScore(r,batting)


    def updateBases(self,bases,result,batter,batting,outs,buffer):
        RBI = 0
        runs = 0
        toRemove = []
        
        if result in ["1","2", "3", "o", "r", "f"]:
            if result in ["o","r"]: 
                outs += 1 
                if outs==3: return bases, outs, runs 
            else: 
                bases.append(batter)
            for player in bases:
                onB = "np"
                while onB != "y" and onB !="n": 
                    onB = input(f"Is {player} still on base? (y/n): ")
                if onB == "n": 
                    score = "np"
                    while score != "s" and score != "o": 
                        score = input(f"Did {player} score or get out? (s/o)")
                    if score == "s": 
                        RBI += 1 
                        buffer.append(partial(batting.stats.recordBatterEvent,"R",1,player))
                        #batting.stats.recordBatterEvent("R",1,player)
                        runs += 1 
                    else: 
                        outs += 1 
                        if outs == 3: break
                    toRemove.append(player)
            for player in toRemove:
                bases.remove(player)

            """
        if result == "o" or result == "r": 
            outs += 1 
            if outs == 3: return bases,outs,runs
            for player in bases:
                onB = "np"
                while onB != "y" and onB !="n": 
                    onB = input(f"Is {player} still on base? (y/n): ")
                if onB == "n": 
                    score = "np"
                    while score != "s" and score != "o": 
                        score = input(f"Did {player} score or get out? (s/o)")
                    if score == "s": 
                        RBI += 1 
                        batting.stats.recordBatterEvent("R",1,player)
                        runs += 1 
                    else: 
                        outs += 1 
                        if outs == 3: break
                    toRemove.append(player)
            for player in toRemove: 
                bases.remove(player)
                
        if result == "f": 
            bases.append(batter)
            toRemove = []
            for player in bases:
                onB = "np"
                while onB != "y" and onB !="n": 
                    onB = input(f"Is {player} still on base? (y/n): ")
                if onB == "n": 
                    score = "np"
                    while score != "s" and score != "o": 
                        score = input(f"Did {player} score or get out? (s/o)")
                    if score == "s": 
                        RBI += 1 
                        batting.stats.recordBatterEvent("R",1,player)
                        runs += 1 
                    else: 
                        outs += 1 
                        if outs == 3: return bases,outs,runs
                    toRemove.append(player)
            for player in toRemove: 
                bases.remove(player)
            """
        
        if result == "4":
            buffer.append(partial(batting.stats.recordBatterEvent,"R",1,batter))
            #batting.stats.recordBatterEvent("R",1,batter)
            RBI += 1
            runs += 1
            for player in bases: 
                #batting.stats.recordBatterEvent("R",1,player)
                buffer.append(partial(batting.stats.recordBatterEvent,"R",1,player))
                RBI += 1 
                runs += 1 
            bases = []

        if result == "w": 
            if len(bases) == 3: 
                buffer.append(partial(batting.stats.recordBatterEvent,"R",1,bases.pop(0)))
                #batting.stats.recordBatterEvent('R', 1, bases.pop(0))
                RBI += 1
                runs += 1 
            bases.append(batter)
        if result == "k":
            outs += 1 

        if RBI: 
            buffer.append(partial(batting.stats.recordBatterEvent,"RBI",RBI,batter))
            #batting.stats.recordBatterEvent("RBI",RBI, batter)

        return bases, outs, runs


    def updateScore(self,runs, team): 
        home = team.home
        leading_0 = self.getLeading()
        if home: 
            self.home_score += runs 
        else: 
            self.away_score += runs 
        leading_now = self.getLeading()
        if leading_0 != leading_now:
            if leading_now == "Home": 
                self.pitch_win = self.home.pitcher
                self.pitch_loss = self.away.pitcher
            else:
                self.pitch_win = self.away.pitcher
                self.pitch_loss = self.home.pitcher

    def getLeading(self): 
        if self.home_score == self.away_score: 
            return None
        if self.home_score > self.away_score: 
            return "Home"
        else: 
            return "Away"
    
    def wAndl(self):
        if self.home_score > self.away_score: 
            self.home.stats.recordPitcherEvent("W",1,self.pitch_win)
            self.away.stats.recordPitcherEvent("L",1,self.pitch_loss)
        else: 
            self.home.stats.recordPitcherEvent("L",1,self.pitch_loss)
            self.away.stats.recordPitcherEvent("W",1,self.pitch_win)



    def updateBoxScore(self,runs,team):
         ing = ((self.current_inning) // 2 ) + 1
         self.box_score.loc[team.name,ing] = runs
        

    def getAtBatResult(self):
        print("What was the result of the at bat?")
        print("Press 1 ==> single")
        print("Press 2 ==> double")
        print("Press 3 ==> triple")
        print("Press 4 ==> home run")
        print("Press r ==> robbed HR")
        print("Press f ==> fielder's choice")
        print("Press w ==> walk")
        print("Press k ==> strikeout")
        print("Press o ==> out(s)")
        print("Press u ==> Undo previous action")

        while True: 
            res = input("")
            if res in ["1","2","3","4","w", "o", "k", "r", "f", 'u']:
                return res
            else: 
                print("Enter a valid outcome: ")

  
    def getPitcher(roster): 
        while True: 
            pitch = input("Who is pitching: ")
            if pitch in roster: 
                print(f"{pitch} is pitching: ")
                break
            else: 
                print("Please print a valid pitcher")
        return pitch


    def play(self): 
        self.home.stats.recordPitcherEvent("GS",1,self.home.pitcher)
        self.away.stats.recordPitcherEvent("GS",1,self.away.pitcher)
        while not self.gameOver(): 
            print("==================\n")
            if self.current_inning % 2 == 0: 
                if self.current_inning >= self.innings: 
                    self.addBox()
                batting = self.away
                pitching = self.home
                print(f"Top of the {(self.current_inning // 2) +1} ")
            else: 
                batting = self.home
                pitching = self.away
                print(f"Bottom of the {(self.current_inning//2) + 1}")
            print(f"Score: {self.home.name} - {self.home_score} {self.away_score} - {self.away.name}")
            print(f"{pitching.name} is pitching, {batting.name} is batting")
            print("==================\n")
            flag = self.simhalfing(batting,pitching)
            if flag: 
                print("Game is over!")
                break
            self.current_inning += 1 

    def finalBox(self,home,away): 
        home_hits = 0 
        away_hits = 0
        for event in ["Single", "Double", "Triple", "HR"]: 
            home_hits += home.stats.hitting[event].sum()
            away_hits += away.stats.hitting[event].sum()
        home_runs = home.stats.hitting["R"].sum()
        away_runs = away.stats.hitting["R"].sum()
        self.box_score["R"] = [away_runs, home_runs]
        self.box_score['H'] = [away_hits,home_hits]