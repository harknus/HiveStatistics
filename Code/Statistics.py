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
        
    def hasPlayerToProfile(self):
        return hasattr(self, 'playerToProfile')
        
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
        
        csvStr  = 'White opening, Black counter, , Hive-PLM openings \n'
        csvStr += 'white win rate, black win rate \n'
               
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
            csvStr1 = tmp[:tmp.find(' ')]
            csvStr2 = str(sublist[0])
            for op in sublist[1]:
                name = op.getName()
                csvStr1 += ',' + name[name.find('b'):]
                csvStr2 += ',' + str(op.getStatistics()['PercentBlackWins']/100)
            
            csvStr += csvStr1 + '\n'
            csvStr += csvStr2 + '\n'
                       
        #Write to file
        file = open(savePath, 'w+', encoding="utf-8")
        file.write(csvStr)
        file.close()
    
    def exportPlayerStatistics(self, folder):
        savePath = folder + self.playerToProfile + '.csv'
        
        #Header
        csvStr  = self.playerToProfile + 'statistics - two bug opening \n'
        csvStr += 'White opening (player) - Black counter, Fraction of player wins, Fraction of player losses, Fraction of draws, Nr of games, List of games won, List of games lost, List of games drawn \n'
        
        #Extract all statistics from the openings
        #sort the data on name
        sortedOpeningList = sorted(self.openingStatList, key=lambda x: x.getName(), reverse=False)
        for op in sortedOpeningList:
            csvStr += op.getPlayerAsWhiteCSVData()
            
        csvStr += '\n\n'
        csvStr += 'White opening - Black counter (player), Fraction of player wins, Fraction of player losses, Fraction of draws, Nr of games, List of games won, List of games lost, List of games drawn \n'
        
        for op in sortedOpeningList:
            csvStr += op.getPlayerAsBlackCSVData()
        
        #get the Player win fractions as a matrix, now we need to do similar 
        #to the summary statistics to get the good formatting output
        #Start with the player being white
        csvStr += '\n\n'
        csvStr += 'Player statistics for playing white \n'
        subLists = list()# this is a nested list
        wBugs = ['wM', 'wL', 'wP', 'wG', 'wA', 'wB', 'wS']
        for wBug in wBugs:
            openings = [x for x in sortedOpeningList if wBug in x.getName()]
            #now calculate the player win rate as white for this white opening
           
            nrGames = 0
            nrWhiteWinsAsWhite = 0
            for op in openings:
                stat = op.getPlayerStatistics()
                nrGames += stat['TotalNrGamesAsWhite']
                nrWhiteWinsAsWhite += stat['NrWinsAsWhite']
            if nrGames == 0:
                playerAsWhiteWinRatio = 0
            else:
                playerAsWhiteWinRatio = nrWhiteWinsAsWhite / nrGames
                #Store it as tuples in the list
                subLists.append( (playerAsWhiteWinRatio, openings, nrGames) )
        
        sortedSubLists = sorted(subLists,  key=lambda x: x[0], reverse=True)
        for sublist in sortedSubLists:
            sublist[1].sort(key=lambda x: x.getPlayerStatistics()['NrWinsAsWhite'], reverse = True)
            tmp = sublist[1][0].getName()
            cvsStr1 = tmp[:tmp.find(' ')]
            cvsStr2 = str(sublist[0])
            for op in sublist[1]:
                name = op.getName()
                cvsStr1 += ',' + name[name.find('b'):]
                stat = op.getPlayerStatistics()
                if stat['TotalNrGamesAsWhite'] != 0:
                    cvsStr2 += ',' + str(stat['NrWinsAsWhite']/stat['TotalNrGamesAsWhite'])
                else:
                    cvsStr2 += ', 0'
                    

            cvsStr1 += ', Total nr games'
            cvsStr2 += ',' + str(sublist[2])

            csvStr += cvsStr1 + '\n'
            csvStr += cvsStr2 + '\n'
        
        #Then do the same for player being black
        csvStr += '\n'
        csvStr += 'Player statistics for playing black \n'
        
        subLists = list()# this is a nested list
        bBugs = ['bM', 'bL', 'bP', 'bG', 'bA', 'bB', 'bS']
        for bBug in bBugs:
            openings = [x for x in sortedOpeningList if bBug in x.getName()]
            #now calculate the player win rate as white for this white opening
           
            nrGames = 0
            nrWhiteWinsAsBlack = 0
            for op in openings:
                stat = op.getPlayerStatistics()
                nrGames += stat['TotalNrGamesAsBlack']
                nrWhiteWinsAsBlack += stat['NrWinsAsBlack']
            if nrGames == 0:
                playerAsBlackWinRatio = 0
            else:
                playerAsBlackWinRatio = nrWhiteWinsAsBlack / nrGames
                #Store it as tuples in the list
                subLists.append( (playerAsBlackWinRatio, openings, nrGames) )
        
        sortedSubLists = sorted(subLists,  key=lambda x: x[0], reverse=True)
        for sublist in sortedSubLists:
            sublist[1].sort(key=lambda x: x.getPlayerStatistics()['NrWinsAsBlack'], reverse = True)
            tmp = sublist[1][0].getName()
            cvsStr1 = tmp[:tmp.find(' ')]
            cvsStr2 = str(sublist[0])
            for op in sublist[1]:
                name = op.getName()
                cvsStr1 += ',' + name[name.find('b'):]
                stat = op.getPlayerStatistics()
                if stat['TotalNrGamesAsBlack'] != 0:
                    cvsStr2 += ',' + str(stat['NrWinsAsBlack']/stat['TotalNrGamesAsBlack'])
                else: 
                    cvsStr2 += ',0'

            cvsStr1 += ', Total nr games'
            cvsStr2 += ',' + str(sublist[2])

            csvStr += cvsStr1 + '\n'
            csvStr += cvsStr2 + '\n'
        
        
        file = open(savePath, 'w+', encoding="utf-8")
        file.write(csvStr)
        file.close()