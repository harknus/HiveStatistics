#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 18 10:14:04 2020

@author: epenjos
"""
import glob2
import time
#import webbrowser
from HiveGame_class import HiveGame, testHiveGameClass
from Position import testPositionClass
from Statistics import Statistics
from Opening import testOpeningStatistics


#Measure time
tic = time.perf_counter()

#Running all implemented tests
runTests = True
if runTests : 
    print("Running tests on Hive classes")
    testPositionClass()
    testHiveGameClass()
    testOpeningStatistics()
    print("All tests passed")

print("Starting Hive game analyzis...")

#print(listOfGames)
#print(listOfGames[0])

# game = HiveGame.importOpeningFromBSFile(listOfGames[3])
# #game = HiveGame().importOpeningFromBSFile('../Hive-games/T!HV-Fraslineco92-RoXar-2020-06-12-1659.sgf')
# # print (game.name)
# # print (game.pieces)

# webbrowser.open(str( game ))
# webbrowser.open(str( game.toStandardPosition() ))

# # To check the validity of a solution go to:
# # https://entomology.appspot.com/hive.html?game=HcZJZtMYnRGsFtEtcdnQUQ&move=11

# Start processing of all files in the subdirectories 
# of the Hive-games directiory, compare and build clases and collecting 
# statistics

listOfGames = glob2.glob('../Hive-games/**/*.sgf')
#listOfGames = glob2.glob('../Hive-games_tmp/**/*.sgf')
#listOfGames.sort()

#pre-filter the games
filterOnPlayers = True
removeRobots = False

if filterOnPlayers :
    #player = 'Gandac'
    # players = ['Frasco92']
    #players = ['Loizz']
    #players = ['HappyKiwi']
    #players = ['Eucalyx']
    players = ['Quodlibet']
    
    #players = ['Eucalyx', 'Gandac', 'Frasco92', 'Loizz', 'ringersoll', \
               # 'davideg', 'Quodlibet', 'fbaumann', 'tzimarou', 'stepanzo', \
               # 'HappyKiwi', 'Jewdoka', 'lambda22', 'dube', 'nevir', \
               # 'saltylick', 'csigeee', 'dube', 'MaxShark', 'stepanzo',\
               # 'tzimarou', 'VYCMajor', 'fbaumann', 'Pseudomon', 'ClaudiuMe',\
               # 'hawk81']
    filteredListOfGames = list()
    for p in players: 
        filteredListOfGames.extend([k for k in listOfGames if p in k])
    
    
    #remove duplicate games found
    filteredListOfGames = list(dict.fromkeys(filteredListOfGames))
    listOfGames = filteredListOfGames


if removeRobots : 
    #remove Weakbot, Dumbot, Smartbot, from the statistics
    filteredListOfGames = list()
    robots = ['WeakBot','Dumbot','SmartBot']
    for g in listOfGames: 
        if not any(x in g for x in robots):
            filteredListOfGames.append(g)
    listOfGames = filteredListOfGames

#-------START-ANALYSING----
stat = dict() #Initalize the statistics dictionary
totNrOfGames = len(listOfGames)

checkOnlyPLM = True
checkOnlyTournamentRuleGames = True

# type of analysis classification
analysisType = 'TwoBugOpening'
#analysisType = '8 first moves openings'


for index, gamePath in enumerate(listOfGames):
    if index % 1000 == 0:
        print('Progress:' + '{0:.2f}'.format(100*index/totNrOfGames) +'%')
    
    if analysisType == 'TwoBugOpening':
        nextGame = HiveGame().importFirstTwoPiecesFromBSFile(gamePath, checkOnlyPLM, checkOnlyTournamentRuleGames)
    else:
        nextGame = HiveGame().importOpeningFromBSFile(gamePath).toStandardPosition()

    #Skip malformatted games   
    if (nextGame == None) or (not hasattr(nextGame, 'gameResult')):
        continue #skip the rest of this iteration in the loop
    
    typeKey = nextGame.gameType
    if typeKey == 'hive-plm':
        typeKey = 'Hive-PLM' #Just to make the output prettier
    if not typeKey in stat:
        stat[typeKey] = Statistics(typeKey); #Create a new statistics class for the game type
    
    stat[typeKey].processGame(nextGame)


toc = time.perf_counter()
processingTime = toc-tic

#output the statistics to console

totalNrOfProcessedGames = 0;
for key in stat:
   totalNrOfProcessedGames += stat[key].totalNrGames

print("Classification" + analysisType)
print("Total number of game files: " + str(totNrOfGames))
print("Total number of games processed: " + str(totalNrOfProcessedGames) )
print("Number of games skipped: " + str(totNrOfGames - totalNrOfProcessedGames) )
#print(stat)
print("Processing time: " + '{0:.2f}'.format(processingTime/60) + " min")

   
openings = stat['Hive-PLM'].openingStatList
openingsSorted = sorted(openings, key=lambda x: x.totalNrGames(), reverse=True)
#the 30 most popular openings
whiteWinSort = sorted(openingsSorted[0:30], key=lambda x: x.getStatistics()['PercentWhiteWins'], reverse=True)
blackWinSort = sorted(openingsSorted[0:30], key=lambda x: x.getStatistics()['PercentBlackWins'], reverse=True)

#print (str(whiteWinSort))
#print (str(blackWinSort))

#Save the results to a .csv file
if analysisType == 'TwoBugOpening':
    
    filePath = "../Statistics/TwoBugOpeningStatistics.csv"
    stat['Hive-PLM'].exportSummaryStatistics("../Statistics/TwoBugSummaryStatistics.csv");
else:
    filePath = "../Statistics/8-moveOpeningStatistics.csv"

stat['Hive-PLM'].exportCSVFile(filePath)

