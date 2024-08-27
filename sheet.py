from numbers_parser import Document
import pandas as pd 


class Sheet(): 
    def __init__(self,path):
        self.path = path
        sheet = Document(path)
        self.pitching = self.getPitching(sheet)
        self.hitting = self.getHitting(sheet)
        self.bat_d = self.getDictBat()
        self.pitch_d = self.getDictPitch()

        
    def getPitching(self,sheet):
       pitch =  sheet.sheets[1].tables[0]
       data = pitch.rows(values_only=True)
       df = pd.DataFrame(data[1:], columns=data[0])
       df.iloc[:] = 0
       return df

    def getHitting(self,sheet): 
       hit =  sheet.sheets[0].tables[0]
       data = hit.rows(values_only=True)
       df = pd.DataFrame(data[1:], columns=data[0])
       df.iloc[:] = 0
       #df.set_index('Batter', inplace=True)
       return df
    
    def addPitcher(self,new, flag): 
        #pdb.set_trace()
        if flag:
            stats = [0] * 10
            self.pitching.loc[new] = stats
        elif new not in self.pitching.index:
            stats = [0] * 10
            self.pitching.loc[new] = stats
            
   
    def initPitcher(self,name): 
        self.pitching['Pitcher'] = name
        self.pitching.set_index('Pitcher', inplace=True)
    

    def outsToIP(self): 
       self.pitching['IP'] = self.pitching['IP'].apply(self.outs_map)
    
    def outs_map(self,value):
        return str(value // 3) + "." + str(value %3) 


    def setRoster(self,roster,name):
        self.hitting.at[0,"Batter"] = name
        count = 1
        for player in roster: 
            self.hitting.at[count,"Batter"] = player
            count += 1
        self.hitting.at[count,"Batter"] = "Total"
        self.hitting.set_index('Batter', inplace=True)


    def getDictBat(self):
        d = {
            "1" : "Single",
            "2" : "Double",
            "3" : "Triple",
            "4" : "HR",
            "w" : "BB",
            "k" : "SO",
            "r" : "R_HR"
        }
        return d
    
    def getDictPitch(self): 
        d = {
            "1" : "H",
            "2" : "H",
            "3" : "H",
            "4" : "HR",
            "w" : "BB",
            "k" : "SO"
        }
        return d
        
    def recordBatterEvent(self,event,value,player): 
        if event in self.bat_d: event = self.bat_d[event]
        cell_value = self.hitting.loc[player,event]
        new_val = int(cell_value) + value
        self.hitting.loc[player, event] = new_val

    
    def recordPitcherEvent(self,event,value,player): 
        if event in self.pitch_d: event = self.pitch_d[event]
        if event == "IP":
            cell_value = self.pitching.loc[player,event]
            new_val = int(cell_value) + value
            self.pitching.loc[player, event] = new_val
        else: 
            if event == "HR":
                self.recordPitcherEvent("H",1,player)
            cell_value = self.pitching.loc[player,event]
            new_val = int(cell_value) + value
            self.pitching.loc[player, event] = new_val
