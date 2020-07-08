# -*- coding: utf-8 -*-
"""
Created on Sun Jun 28 17:37:57 2020

@author: jonas_d6wnu18
"""
import webbrowser
import ntpath
import os
from HiveGame_class import HiveGame

class Opening :
    
    def __init__(self):
        self.openingGame = None
        self.whiteWinGamesPaths = list() #File paths to the games
        self.blackWinGamesPaths = list()
        self.drawGamesPaths = list()
        
        
    def totalNrGames(self):
        return len(self.whiteWinGamesPaths) \
               + len(self.blackWinGamesPaths) \
               + len(self.drawGamesPaths)
        
    def getStatistics(self):
        nrWhiteWins = len(self.whiteWinGamesPaths)
        nrBlackWins = len(self.blackWinGamesPaths)
        nrDraws     = len(self.drawGamesPaths)
        totalNrGames = nrWhiteWins + nrBlackWins + nrDraws
        
        results = {'TotNrGames'       : totalNrGames, \
                   'PercentWhiteWins' : 100 * nrWhiteWins / totalNrGames, \
                   'PercentBlackWins' : 100 * nrBlackWins / totalNrGames, \
                   'PercentDraws'     : 100 * nrDraws     / totalNrGames }
        return results
        
    def __str__(self):
        stat = self.getStatistics()
        totNr = stat['TotNrGames']
        whiteWins = stat['PercentWhiteWins']
        blackWins = stat['PercentBlackWins']
        draws = stat['PercentDraws']
        gameName = self.openingGame.name
        return '{0:s} :: N={1:d} ww={2:.0f}% bw={3:.0f}% d={4:.0f}% \n'\
            .format(gameName, totNr, whiteWins, blackWins, draws)
    
    def __repr__(self):
        return self.__str__()
    
    def getRepresentativeGame(self):
        return self.openingGame

    def addGameToStat(self, aGame):
        #When the first game is added store the loaded game opening
        if self.openingGame == None:
            self.openingGame = aGame
        
        #Add game path to correct list
        if aGame.gameResult == 'white win':
            self.whiteWinGamesPaths.append(aGame.fileName)
        elif aGame.gameResult == 'black win':
            self.blackWinGamesPaths.append(aGame.fileName)
        else : 
            #RE[The game is a draw]
            self.drawGamesPaths.append(aGame.fileName)

    def getEntURL(self):
        baseURL = self.openingGame.getEntString()
        gameName = self.openingGame.name
        stat = self.getStatistics()
        totNr = stat['TotNrGames']
        whiteWins = stat['PercentWhiteWins']
        blackWins = stat['PercentBlackWins']
        draws = stat['PercentDraws']
        # %25 = '%'
        # %20 = ' ' 
        title = '{0:s}%20::%20N:{1:d}%20whitewin:{2:.0f}%25%20blackwin:{3:.0f}%25%20draw:{4:.0f}%25'\
            .format(gameName, totNr, whiteWins, blackWins, draws)
        
        return baseURL + title

    def getCSVResultString(self):
        # protect ',' symbols by putting "" around the cells
        stat = self.getStatistics()
        
        # Format:
        #         openingName, entomologyURL, totalNrGames, 
        #         nrWhiteWinGames, white win percentage, 
        #         nrBlackWinGames, black win percentage, 
        #         nrDrawGames, draw percentage, 
        #         listOfWhiteWinGames, listOfBlackWinGames, listOfDrawnGames
        
        #If only filtering on the first 2 opening bugs then auto-name the opening
        if len(self.openingGame.pieces) == 2:
            
            for p in self.openingGame.pieces:
                if p.color == 'white':
                    wstr = p.name
                else:
                    bstr = p.name
            result = wstr + ' - ' + bstr + ','
        else:     
            result = self.openingGame.name + ','
            
        result += self.getEntURL() + ','
        result += str(stat['TotNrGames']) + ','
        result += str(len(self.whiteWinGamesPaths)) + ','
        result += str(stat['PercentWhiteWins']) + ','
        result += str(len(self.blackWinGamesPaths)) + ','
        result += str(stat['PercentBlackWins']) + ','
        result += str(len(self.drawGamesPaths)) + ','
        result += str(stat['PercentDraws']) + ','
        
        result += '"'
        for l in self.whiteWinGamesPaths:             
            result += os.path.splitext(ntpath.basename(l))[0] + ', '
                
        result += '","'
        for l1 in self.blackWinGamesPaths:
            result += os.path.splitext(ntpath.basename(l1))[0] + ', '
        
        result += '","'
        for l2 in self.drawGamesPaths:
            result = result + os.path.splitext(ntpath.basename(l2))[0] + ', '
        result += '"'
        
        return result

    def visualize(self):
        
        url = self.getEntURL()
        webbrowser.open(url)
        
        result = 'Games won by white ({0:d}): \n'.format(len(self.whiteWinGamesPaths))
        for l in self.whiteWinGamesPaths:             
            result = result + os.path.splitext(ntpath.basename(l))[0] + '\n'
            
        result = result + 'Games won by black ({0:d}): \n'.format(len(self.blackWinGamesPaths))
        for l1 in self.blackWinGamesPaths:
            result = result + os.path.splitext(ntpath.basename(l1))[0] + '\n'
        
        result = result + 'Games resulting in draw ({0:d}): \n'.format(len(self.drawGamesPaths))
        for l2 in self.drawGamesPaths:
            result = result + os.path.splitext(ntpath.basename(l2))[0] + '\n'
        
        print(result)
        