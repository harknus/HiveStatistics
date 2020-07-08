#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 27 08:17:24 2020

Used to collect the statistics of the games into classes

@author: epenjos
"""
from Opening import Opening

class Statistics : 
    def __init__(self, gameType):
        self.gameType = gameType
        self.totalNrGames = 0;
        self.openingStatList = list() #holds the statistics for the openings for the same index
               
        
    def processGame(self, game):
        self.totalNrGames += 1
        
        found = None
        for openingStat in self.openingStatList:
            opening = openingStat.getRepresentativeGame()
            if game.isEqualTo(opening) == True:
                openingStat.addGameToStat(game)
                found = True
                break
        
        if not found:
            #create a new Opening statistics object
            newOpeningStatistics = Opening()
            newOpeningStatistics.addGameToStat(game)
            self.openingStatList.append(newOpeningStatistics)
        
    def __str__(self):    
        retvar = ''
        for stat in self.openingsWithMoreThanXGames(5):
           retvar = retvar + str(stat)
        
        return '\n' + retvar
    
    def __repr__(self):
        return self.__str__()
    
    def openingsWithMoreThanXGames(self, X):
        retval = list()
        for op in self.openingStatList:
            if op.totalNrGames() > X:
                retval.append(op)
                
        return retval
    
    def exportCSVFile(self, savePath):
        # CSV format:
        # 1st line: game type 
        # 2nd line: openingName,entomologyURL, totalNrGames, 
        #           nrWhiteWinGames, white win percentage, 
        #           nrBlackWinGames, black win percentage, 
        #           nrDrawGames, draw percentage, 
        #           listOfWhiteWinGames, listOfBlackWinGames, listOfDrawnGames
        # following lines data
        
        file = open(savePath, 'w+', encoding="utf-8")
        
        csvStr  = 'Game Type:,' + self.gameType + '\n'
        csvStr += 'TotNrGames:,' + str(self.totalNrGames) + '\n'
        csvStr += 'Opening name, Entomology URL, Total nr of games, '
        csvStr += 'Nr white wins, White win percentage, '
        csvStr += 'Nr black wins, Black win percentage, '
        csvStr += 'Nr draws, Draw percentage, '
        csvStr += 'List of white win games, List of black win games, List of drawn games\n'
        
        file.write(csvStr)
        
        for op in self.openingStatList:
            file.write(op.getCSVResultString() + '\n')
        
        #return csvStr
        
        #write to file
        file.close()

        
        