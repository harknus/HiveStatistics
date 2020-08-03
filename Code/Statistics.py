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
               
    def setPlayerToProfile(self, player):
        self.playerToProfile = player
        
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
            if  hasattr(self, 'playerToProfile'):
                newOpeningStatistics.setPlayerToProfile(self.playerToProfile)
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
        
        file.close()

    def exportSummaryStatistics(self, savePath):
        # only works for the 2-bug opening statistics
        # CSV format:
        # 1st line: titles
        # 2nd line: more titles
        # 2n   line: bug titles white opening and black counters sorted in order of performance
        # 2n+1 line: win percentages
        
        cvsStr  = 'White opening, Black counter, , Hive-PLM openings \n'
        cvsStr += 'white win rate, black win rate \n'
               
        #sort the data and extract out the white win percenatges given an opening
        sortedOpeningList = sorted(self.openingStatList, key=lambda x: x.getName(), reverse=False)
        
        #To extract out the sublist
        subLists = list()# this is a nested list
        wBugs = ['wM', 'wL', 'wP', 'wG', 'wA', 'wB', 'wS']
        for wBug in wBugs:
            openings = [x for x in sortedOpeningList if wBug in x.getName()]
            #now calculate the white win rate for this white opening
           
            nrGames = 0
            nrWhiteWins = 0
            for op in openings:
                nrGames += op.totalNrGames()
                nrWhiteWins += op.getNrWhiteWins()
            if nrGames == 0:
                whiteWinRatio = 0
            else:
                whiteWinRatio = nrWhiteWins / nrGames
                #Store it as tuples in the list
                subLists.append( (whiteWinRatio, openings) )
        
        #sort the subLists on first item in the tuple (white win rate)
        sortedSubLists = sorted(subLists,  key=lambda x: x[0], reverse=True)
        for sublist in sortedSubLists:
            sublist[1].sort(key=lambda x: x.getStatistics()['PercentBlackWins'], reverse = True)
            tmp = sublist[1][0].getName()
            cvsStr1 = tmp[:tmp.find(' ')]
            cvsStr2 = str(sublist[0])
            for op in sublist[1]:
                name = op.getName()
                cvsStr1 += ',' + name[name.find('b'):]
                cvsStr2 += ',' + str(op.getStatistics()['PercentBlackWins']/100)
            
            cvsStr += cvsStr1 + '\n'
            cvsStr += cvsStr2 + '\n'
                       
        #Write to file
        file = open(savePath, 'w+', encoding="utf-8")
        file.write(cvsStr)
        file.close()