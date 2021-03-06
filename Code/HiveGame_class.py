#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 18 10:31:36 2020

@author: epenjos
"""
import os
import re
import webbrowser

from Piece_class import Piece
from Position import Position

def findBetween(s, start, end):
    return s[s.find(start)+len(start):s.rfind(end)]

#Remove the number from pieces that is only one
def cleanPieceName (s):
    matches = {'L','M','Q','P'}
    if any(x in s for x in matches) :
        #remove the nunbering of the piece if present
        return re.sub(r'[0-9]+', '', s)
    else:
        return s
        

class HiveGame:
    #str name
    #list listOfBugs
    
    def __init__(self):
        #empty for now
        pass
    
    #check when to stop reading the game
    def shouldContinueMovingBased(self, thePiece, breakConditionType): 
        if breakConditionType == 0:
            #quit before black moves the first piece
            if 'w' in thePiece.name : 
                return True
            else : 
                return None
        elif breakConditionType == 1:
            #quit once the first piece irrespective of color moves
            return None
        else:
            #Don't quit using moving piece condition
            return True
   
    def shouldContinueNrBased(self, maxNrPieces, breakConditionType):
        if breakConditionType != 2:
            return True
        else:
            # continue until maxNr of pieces has been imported
            if len(self.pieces) >= maxNrPieces:
                return None
            else:
                return True
            
    def shouldContinueNrMoves(self, currentMoveNr, lastMoveNrToInclude, breakConditionType):
        if breakConditionType == 3 : 
            if currentMoveNr >= lastMoveNrToInclude :
                return None
            else:
                return True
        else:
            return True
            
    #returns the first piece found with the name by default
    #if disregardPieceNumber = True and more than 1 piece match a list of 
    #the matching pieces is returned
    def getPieceByName(self, aName, disregardPieceNumber=False):
        
        if disregardPieceNumber == False :
            return next((x for x in self.pieces if x.name == aName), None)
        else :
            if not any(char.isdigit() for char in aName): 
                return next((x for x in self.pieces if x.name == aName), None)
            else: 
                aName = re.sub(r"\d+", "", aName)
                retlist = [x for x in self.pieces if re.sub(r"\d+", "", x.name) == aName]
                if len(retlist) == 0:
                    return None
                if len(retlist) == 1:
                    return retlist[0]
                else :
                    return retlist
                
            
    #use the file name to instantiate the game
    def importOpeningFromBSFile(self, aFileName):
        
        #Ugly hack parameters
       
        #breakConditionType = 0 # break just before black moves
        #breakConditionType = 1 # break just before any piece move
        #breakConditionType = 2 # break once a max nr of pieces has been imported
        breakConditionType = 3 # include only a certain number of moves
        maxNrPieces = 8
        lastMoveNrToInclude = 8
        checkOnlyPLM = True
        
        
        self.pieces = set() # Storage for the unordered set of bugs in play
        self.fileName = aFileName;
        tmp = os.path.basename(aFileName)
        self.name = os.path.splitext(tmp)[0]
        
        #Read the file and import the opening
        fileObject = open(aFileName, 'r',  encoding='utf-8', errors='ignore')
        currentMoveNr = 0
        for line in fileObject:
            
            #If we should only process PLM games check if this 
            #game is a PLM game, if not skip it and stop reading
            if "SU[" in line:
                self.gameType = findBetween(line, "SU[", "]").lower()
                #Skip all games that are not PLM
                if checkOnlyPLM and self.gameType != 'Hive-PLM'.lower():
                    break
                
            if self.findOutGameResult(line) == None:
                break
                
            #building the opening state
            
            if any(x in line for x in ["move", "dropb", "pdropb", "Move", "Dropb", "Pdropb"]):
                #building the opening state
                currentMoveNr += 1
                parts =  line.split()
                #print(line)
                if ("dropb" in line) or ("pdropb" in line) \
                    or ("Dropb" in line) or ("Pdropb" in line):    
                    #; P1[5 dropb bL1 M 12 /wM]
                    #added pdropb and support for newer files where 
                    #actions/moves are capitalized in the .sgf files
                    newPieceName = cleanPieceName(parts[3])
                    #print(parts[3] +" => "+ newPieceName)
                    placement = parts[6][:-1]
                    coordinates = parts[4] + ' ' + parts[5]
                else:
                    #; P0[11 move W wA1 O 14 wS2-]
                    newPieceName = cleanPieceName(parts[4])
                    placement = parts[7][:-1]
                    coordinates = parts[5] + ' ' + parts[6]
                    
                placement = placement.replace("\\\\", "\\") #clean the placement from "//"='////'
                #print(newPieceName, placement)
                
                #New placement of piece or update of an already moved piece
                
                thePiece = self.getPieceByName(newPieceName)
                
                #if the piece was not found then add a new piece
                if thePiece == None :
                    if 'w' in newPieceName : color = 'white'
                    else : color = 'black'
                    #Level = 0 for all pieces that have not 
                    #climbed on top of the hive 
                    level = 0; 
                    newPiece = Piece(newPieceName, color, coordinates, level)
                    self.pieces.add(newPiece)
                    if len(self.pieces) == 1:
                        self.firstPlacedPosition  = newPiece.position
                    if len(self.pieces) == 2:
                        self.secondPlacedPosition = newPiece.position
                
                else: #not a newly added piece, but a piece to move
                    if self.shouldContinueMovingBased(thePiece, breakConditionType) == True :
                        #print("Moving piece: " + newPieceName + " " + placement)
                        thePiece.moveTo(coordinates)
                    else:
                        break #stop reading the file
                
                #check number of imported pieces is enabled 
                #only used if break condition == 2
                if self.shouldContinueNrBased(maxNrPieces, breakConditionType) == None : 
                    break
                if self.shouldContinueNrMoves(currentMoveNr, lastMoveNrToInclude, breakConditionType) == None :
                    break
                

        #close the file - important
        fileObject.close()
        return self
    
    #Convenience function for avoiding duplication of code
    #Returns None if the game result cannot be obtained.
    def findOutGameResult(self, line):
        #extract the game result, black or white
        if "CM[1,0]" in line:
            self.reversedColors = True
            #print( str(self.name) )
        if "CM[0,1]" in line:
            self.reversedColors = False
        
        if "RE[" in line:
            #Add support for multiple languages
            self.gameResult = findBetween(line, "[","]");
                
        if "P0[id" in line:
            if hasattr(self, 'gameResult') != True:
                #There has been a reading error
                print ("Encoding error in file:" + self.fileName)
                return None
            
            if hasattr(self, 'reversedColors') == True:
                if self.reversedColors == False:
                    self.whitePlayer = findBetween(line, "id \"", "\"]")
                    if self.whitePlayer in self.gameResult \
                        or re.sub(r"\d+", "", self.whitePlayer) in self.gameResult:
                        self.gameResult = "white win"
                else :
                    self.blackPlayer = findBetween(line, "id \"", "\"]")
                    if self.blackPlayer in self.gameResult \
                        or re.sub(r"\d+", "", self.blackPlayer) in self.gameResult:
                        self.gameResult = "black win"
            else: #for older files
                self.whitePlayer = findBetween(line, "id \"", "\"]")
                if self.whitePlayer in self.gameResult \
                        or re.sub(r"\d+", "", self.whitePlayer) in self.gameResult:
                    self.gameResult = "white win"
                        
        if "P1[id" in line:
            if hasattr(self, 'reversedColors') == True:
                if self.reversedColors == False:
                    self.blackPlayer = findBetween(line, "id \"", "\"]")
                    if self.blackPlayer in self.gameResult \
                        or re.sub(r"\d+", "", self.blackPlayer) in self.gameResult:
                        self.gameResult = "black win"
                else : #reversed colors
                    self.whitePlayer = findBetween(line, "id \"", "\"]")
                    if self.whitePlayer in self.gameResult \
                        or re.sub(r"\d+", "", self.whitePlayer) in self.gameResult:
                        self.gameResult = "white win"
            else: #for older files
                self.blackPlayer = findBetween(line, "id \"", "\"]")
                if self.blackPlayer in self.gameResult \
                        or re.sub(r"\d+", "", self.blackPlayer) in self.gameResult:
                    self.gameResult = "black win"
                        
        return True
    
    def getWinningPlayer(self):
        if hasattr(self, 'gameResult'):
            if 'white win' in self.gameResult:
                return self.whitePlayer
            elif 'black win' in self.gameResult:
                return self.blackPlayer
        return 'No winner'
            
    
    def importFirstTwoPiecesFromBSFile(self, aFileName, checkOnlyPLM, onlyTournamentRule):
        self.pieces = set() # Storage for the unordered set of bugs in play
        self.fileName = aFileName;
        tmp = os.path.basename(aFileName)
        self.name = os.path.splitext(tmp)[0]

        #read the file, extract who won, and the first 2 pieces placed
        
        fileObject = open(aFileName, 'r',  encoding='utf-8', errors='ignore')
        currentMoveNr = 0
        for line in fileObject:
            if "SU[" in line:
                self.gameType = findBetween(line, "SU[", "]").lower()
                #Skip all games that are not PLM
                if checkOnlyPLM and self.gameType != 'Hive-PLM'.lower():
                    break
                
            if self.findOutGameResult(line) == None:
                break
            
            if any(x in line for x in ["move", "dropb", "pdropb", "Move", "Dropb", "Pdropb"]):
                currentMoveNr += 1
                parts =  line.split()
                #print(line)
                if ("dropb" in line) or ("pdropb" in line) \
                    or ("Dropb" in line) or ("Pdropb" in line):    
                    #; P1[5 dropb bL1 M 12 /wM]
                    #; P1[131 Pdropb wS1 K 9 /bP]
                    #; P0[110 Dropb wG3 O 11 wM-]
                    newPieceName = cleanPieceName(parts[3])
                    #print(parts[3] +" => "+ newPieceName)
                    placement = parts[6][:-1]
                    coordinates = parts[4] + ' ' + parts[5]
                else:
                    #; P0[11 move W wA1 O 14 wS2-]
                    newPieceName = cleanPieceName(parts[4])
                    placement = parts[7][:-1]
                    coordinates = parts[5] + ' ' + parts[6]
                    
                #clean the placement from "//"='////'
                placement = placement.replace("\\\\", "\\")
                
                #check that tournament rule is upheld
                #no queens as the first 2 pieces placed
                if (onlyTournamentRule == True) and ('Q' in newPieceName) : 
                    break
                
                #check color
                if 'w' in newPieceName : 
                    color = 'white'
                else: 
                    color = 'black'
                
                #Level = 0 for all pieces that have not 
                #climbed on top of the hive 
                level = 0
                newPiece = Piece(newPieceName, color, coordinates, level)

                self.pieces.add(newPiece)
                #Once we've found the first 2 pieces we stop reading the file
                if len(self.pieces) == 2:
                    break
        
        #close the file - important            
        fileObject.close()
        
        #Captures and filters away early resigns
        if len(self.pieces) != 2:
            return None
        
        return self
    
    def __repr__(self):
        return "<Hive game: %s>" % (self.name)
    
    #Generate the entomology-link to visualize the game
    #Use this string and just append any title string at the end then it 
    #becomes a valid URL for visualizing the game state
    def getEntString (self):
        boardString =  '';
        for p in self.pieces:
            boardString += p.getEntString();      
        baseStr = "https://entomology.appspot.com/hive.html?bg=0&color=1&grid=0&label=1&mode=edit&board="
        return baseStr + boardString + "&title="
        
    def __str__(self):
        entStr = self.getEntString()
        titleStr = self.name
        return entStr + titleStr
    
    def visualize(self):
        webbrowser.open( self.__str__() )

    
    #modifies the positions of the pieces to become standard format
    #Symmerty Transformations:
    # - translatios
    # - 60 degree rotations
    # - reflections in x-axis
    def toStandardPosition(self):
        
        #if we compare only the 2 first pieces then don't do anything
        if len(self.pieces) == 2: 
            return self
        
        #To protect against early resign
        if ((len(self.pieces) == 0) or (len(self.pieces) == 1) \
            or (not hasattr(self, 'firstPlacedPosition')) \
            or (not hasattr(self, 'secondPlacedPosition')) \
            or (self.getPieceByName("wQ") == None)\
            or (self.getPieceByName("bQ") == None) ):
            return None
        
        #the first piece placed is white and ensure that it is at (0,0)
        if self.firstPlacedPosition != Position(0,0):
            self.translateGameBy(self.firstPlacedPosition)
            
        #the next piece placed need to be rotated to (1,0)
        # => good that we kept track on which piece was added second!
        if self.secondPlacedPosition == Position(1,-1):
            #rotate game clockwise 60 degrees
            self.rotGame60CW()
                
        elif self.secondPlacedPosition == Position(0,-1):
            #rotate game clockwise 120 degrees
            self.rotGame120CW()
                
        elif self.secondPlacedPosition == Position(-1,0):
            #rotate game 180 degrees
            self.rotGame180()
                
        elif self.secondPlacedPosition == Position(-1,1):
            #rotate game counter-clockwise 120 degrees
            self.rotGame120CCW()
                
        elif self.secondPlacedPosition == Position(0,1):
            #rotate game counter-clockwise 60 degrees
            self.rotGame60CCW();
        
        #Next check if the white queen is above on or below the x-axis
        # in this coordinate system being above the x-axis is equivalent to 
        # having a negative coordinate b
        wQ = self.getPieceByName("wQ")
        if wQ.position.b > 0:
            #then we make a refllection in the x-axis
            self.reflGameXaxis()
            
        elif wQ.position.b == 0:
            #then we check the black queen position if it is above or 
            #below the x-axis
            bQ = self.getPieceByName("bQ")
            if bQ.position.b > 0:
                #If below the line we need a reflection
                self.reflGameXaxis()
        return self
    
    #Functions to translate, rotate and reflect the entire game 
    #Primarily extracted out for testing purposes
    def translateGameBy(self, vector):
        #Translate the game by a vector
        self.firstPlacedPosition  = self.firstPlacedPosition - vector
        self.secondPlacedPosition = self.secondPlacedPosition - vector
        for p in self.pieces:
            p.position = p.position - vector
        return self
    
    def rotGame60CW(self):
        #rotate game clockwise 60 degrees
        self.firstPlacedPosition  = self.firstPlacedPosition.rot60CW()
        self.secondPlacedPosition = self.secondPlacedPosition.rot60CW()
        for p in self.pieces:
            p.position = p.position.rot60CW()
        return self
    
    def rotGame120CW(self):
        #rotate game clockwise 120 degrees
        self.firstPlacedPosition  = self.firstPlacedPosition.rot120CW()
        self.secondPlacedPosition = self.secondPlacedPosition.rot120CW()
        for p in self.pieces:
            p.position = p.position.rot120CW()
        return self
    
    def rotGame180(self):
        #rotate game 180 degrees
        self.firstPlacedPosition  = self.firstPlacedPosition.rot180CCW()
        self.secondPlacedPosition = self.secondPlacedPosition.rot180CCW()
        for p in self.pieces:
            p.position = p.position.rot180CCW()
        return self
    
    def rotGame120CCW(self):
        #rotate game counter-clockwise 120 degrees
        self.firstPlacedPosition  = self.firstPlacedPosition.rot120CCW()
        self.secondPlacedPosition = self.secondPlacedPosition.rot120CCW()
        for p in self.pieces:
            p.position = p.position.rot120CCW()
        return self
    
    def rotGame60CCW(self):
        #rotate game counter-clockwise 60 degrees
        self.firstPlacedPosition  = self.firstPlacedPosition.rot60CCW()
        self.secondPlacedPosition = self.secondPlacedPosition.rot60CCW()
        for p in self.pieces:
            p.position = p.position.rot60CCW()
        return self

    def reflGameXaxis(self):
        #reflects the game in the x-axis
        self.firstPlacedPosition  = self.firstPlacedPosition.reflXaxis()
        self.secondPlacedPosition = self.secondPlacedPosition.reflXaxis()
        for p in self.pieces:
            p.position = p.position.reflXaxis()
        return self

    #Function to evaluate if the game state is equivalent to another state
    def isEqualTo(self, other):
        #Check that the game type is the same, otherwise not relevant to compare
        if self.gameType !=  other.gameType:
            return False
        
        #Check if the two games have the same number of pieces
        if len( self.pieces ) != len( other.pieces ):
            return False
        
        #If only two pieces in the game do only check the names as the 
        #positions have not been rotated properly
        shouldCheckPositions = True
        if len(self.pieces) == 2:
            shouldCheckPositions = False
            
        #Then for every piece in this game find it in the other game 
        #and check if the positions agree
        for p in self.pieces :
            p2 = other.getPieceByName(p.name, True);
            #if the piece is not in the other game => not equal
            if p2 == None: 
                return False
            
            if shouldCheckPositions == True:
                #if several bugs of the same type are found check for 
                #match for one position if so then ok
                if isinstance(p2,list) :
                    equalBugInList = False
                    for piece in p2 : #iterate through the equal-type bugs
                        if piece.position == p.position \
                            and piece.level == p.level:
                           #then we've found the correct bug matching with p
                           equalBugInList = True
                    if equalBugInList == False:
                        return False
                    
                else: #not a list then a single bug
                    #Check position equality
                    if p2.position  != p.position:
                        return False
                
                    #Check the layer of the pieces are equal 
                    #(as some bugs may be on top of the hive)
                    if p2.level != p.level:
                        return False
                
        #If we reach this point the games are equal
        return True

def testHiveGameClass():
    
    
    #testGame = HiveGame('../Hive-games/2019/games-May-21-2019/HV-WeakBot-guest-2019-05-15-2238.sgf')
    #assert testGame.gameResult == 'black win'
    
    #Test that the different functions work as expected.
    gameName1 = '../Hive-games/2020/games-Jun-13-2020/T!HV-Frasco92-RoXar-2020-06-12-1659.sgf'
    gameName2 = '../Hive-games/2019/games-May-21-2019/T!HV-nevir-MaxShark-2019-05-20-2000.sgf'
    game1 = HiveGame().importOpeningFromBSFile(gameName1)
    game1a = HiveGame().importOpeningFromBSFile(gameName1)
    game2 = HiveGame().importOpeningFromBSFile(gameName2)
    
    assert not game1.isEqualTo(game2)
    assert not game1.toStandardPosition().isEqualTo(game2.toStandardPosition())
    
    #Load the same game twice
    game1 = HiveGame().importOpeningFromBSFile(gameName2)
    game2 = HiveGame().importOpeningFromBSFile(gameName2)
    assert game1.isEqualTo(game2) == True
    assert game1.toStandardPosition().toStandardPosition().isEqualTo(game2.toStandardPosition()) == True
    
    #Need to reset the games once modified
    game1 = HiveGame().importOpeningFromBSFile(gameName1)
    game2 = HiveGame().importOpeningFromBSFile(gameName2)
    
    #Test rotation and back again
    assert game1.rotGame60CCW().rotGame60CW().isEqualTo(game1a) == True
    
    game1 = HiveGame().importOpeningFromBSFile(gameName1)
    game1a = HiveGame().importOpeningFromBSFile(gameName1)
    assert game1.rotGame60CW().rotGame60CCW().isEqualTo(game1a) == True
    
    game1 = HiveGame().importOpeningFromBSFile(gameName1)
    game1a = HiveGame().importOpeningFromBSFile(gameName1)
    assert game1.rotGame60CW().rotGame60CW().isEqualTo(game1a.rotGame120CW()) == True
    
    game1 = HiveGame().importOpeningFromBSFile(gameName1)
    game1a = HiveGame().importOpeningFromBSFile(gameName1)
    assert game1.rotGame120CCW().rotGame120CW().isEqualTo(game1a) == True
    
    game1 = HiveGame().importOpeningFromBSFile(gameName1)
    game1a = HiveGame().importOpeningFromBSFile(gameName1)
    assert game1.reflGameXaxis().reflGameXaxis().isEqualTo(game1a) == True
    
    game1 = HiveGame().importOpeningFromBSFile(gameName1)
    game1a = HiveGame().importOpeningFromBSFile(gameName1)
    assert game1.rotGame180().rotGame180().isEqualTo(game1a) == True
    
    game1 = HiveGame().importOpeningFromBSFile(gameName1)
    game1a = HiveGame().importOpeningFromBSFile(gameName1)
    assert game1.rotGame180().rotGame60CW().rotGame120CW().isEqualTo(game1a) == True
    
    #Test transformation to standard position
    game1 = HiveGame().importOpeningFromBSFile(gameName1)
    game1a = HiveGame().importOpeningFromBSFile(gameName1)
    assert game1.toStandardPosition().isEqualTo(game1a.translateGameBy(Position(-1,0))) == True
    
    game1 = HiveGame().importOpeningFromBSFile(gameName1)
    game1a = HiveGame().importOpeningFromBSFile(gameName1)
    assert game1.isEqualTo(game1a) == True
    game1a.gameType = 'Hive-PL'
    assert not game1.toStandardPosition().isEqualTo(game1a.toStandardPosition())
    
    #test that matching bugs with the same bugtype but name but with different nubmers 
    #matches as equivalent games
    gameName1 = '../Hive-games/2017/games-May-27-2017/HV-iserp-Quodlibet-2017-05-26-1516.sgf'
    game1 = HiveGame().importOpeningFromBSFile(gameName1)
    game2 = HiveGame().importOpeningFromBSFile(gameName1)
    #change the names of the two wA pieces
    wA1 = game2.getPieceByName("wA1")
    wA2 = game2.getPieceByName("wA2")
    wA1.name="wA2"
    wA2.name = "wA1"
    assert game1.isEqualTo(game2) == True
    assert game1.toStandardPosition().isEqualTo(game2.toStandardPosition()) == True
    
    #assert that white won this game
    gameName = '../Hive-games/2020/games-Apr-24-2020/HV-CBerserker-hawk81-2020-04-23-0845.sgf'
    game1 = HiveGame().importOpeningFromBSFile(gameName)
    assert game1.gameResult == "white win"
    
    gameName = '../Hive-games/2015/games-Apr-11-2015/HV-Dumbot-kdladage-2015-04-10-0508.sgf'
    game1 = HiveGame().importOpeningFromBSFile(gameName)
    assert game1.gameResult == "white win"
    assert game1.getWinningPlayer() == 'Dumbot'
    
    
    gameName = '../Hive-games/2020/games-May-5-2020/HV-Rufeo612-WeakBot1-2020-05-04-1609.sgf'
    game1 = HiveGame().importOpeningFromBSFile(gameName)
    assert game1.gameResult == "black win"
    assert game1.getWinningPlayer() == 'WeakBot1'
        
    
    gameName = '../Hive-games/2019/games-Jul-7-2019/T!HV-Eucalyx-dube-2019-06-30-0520.sgf'
    game1 = HiveGame().importOpeningFromBSFile(gameName)
    assert game1.gameResult != "white win" or game1.gameResult != "black win"
    assert game1.getWinningPlayer() == 'No winner'
    
    checkOnlyPLM = True
    checkOnlyTournamentRuleGames = True
    game1 = HiveGame().importFirstTwoPiecesFromBSFile(gameName, checkOnlyPLM, checkOnlyTournamentRuleGames)
    assert game1.gameResult != "white win" or game1.gameResult != "black win"
    assert game1.getWinningPlayer() == 'No winner'