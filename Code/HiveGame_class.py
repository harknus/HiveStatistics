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
            
    
    def getPieceByName(self, aName):
        return next((x for x in self.pieces if x.name == aName), None)
    
    #use the file name to instantiate the game
    def __init__(self, aFileName):
        
        #Fulhack parameters
       
        #breakConditionType = 0 # break just before black moves
        #breakConditionType = 1 # break just before any piece move
        #breakConditionType = 2 # break once a max nr of pieces has been imported
        breakConditionType = 3 # include only a certain number of moves
        maxNrPieces = 8
        lastMoveNrToInclude = 8
        checkOnlyPLM = True
        
        
        self.pieces = set(); # Storage for the unordered set of bugs in play
        self.fileName = aFileName;
        tmp = os.path.basename(aFileName)
        self.name = os.path.splitext(tmp)[0]
        #print(self.name)
        
        
        #Read the file and import the opening
        #Opening is defined as the state just 
        #before the first black move
        fileObject = open(aFileName, 'r', errors='ignore')
        currentMoveNr = 0
        for line in fileObject:
            
            if "SU[" in line:
                self.gameType = findBetween(line, "SU[", "]").lower()
                #Skip all games that are not PLM
                if checkOnlyPLM and self.gameType != 'Hive-PLM'.lower():
                    break
                
            #extract the game result, black or white
            if "RE[" in line:
                #Add support for multiple languages
                self.gameResult = findBetween(line, "[","]");
                    
            if "P0[id" in line:
                if hasattr(self, 'gameResult') != True:
                    #There has been a reading error
                    print ("Encoding error in file:" + aFileName)
                    break
                
                whitePlayer = findBetween(line, "id \"", "\"]")
                if whitePlayer in self.gameResult:
                    self.gameResult = "white win"
                
            if "P1[id" in line:
                blackPlayer = findBetween(line, "id \"", "\"]")
                if blackPlayer in self.gameResult:
                    self.gameResult = "black win"
                
            #building the opening state
            
            if any(x in line for x in ["move", "dropb"]):
                #building the opening state
                currentMoveNr += 1
                parts =  line.split()
                #print(line)
                if "dropb" in line:    
                    #; P1[5 dropb bL1 M 12 /wM]
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
                    #Level 1 for all pieces that have not 
                    #climbed on top of the hive 
                    level = 0; 
                    newPiece = Piece(newPieceName, color, coordinates, level)
                    self.pieces.add(newPiece)
                    if len(self.pieces) == 1:
                        self.firstPlacedPosition  = newPiece.position
                    if len(self.pieces) == 2:
                        #updated here and it doesn't work anymore...
                        #self.secondPiecePlaced = newPiece
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
        #To protect against early resign
        if ((len(self.pieces) == 0) \
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


    def isEqualTo(self, other):
        #Check that the game type is the same, otherwise not relevant to compare
        if self.gameType !=  other.gameType:
            return None
        
        #Check if the two games have the same number of pieces
        if len( self.pieces ) != len( other.pieces ):
            return None
        
        #Then for every piece in this game find it in the other game 
        #and check if the positions agree
        for p in self.pieces :
            p2 = other.getPieceByName(p.name);
            #if the piece is not in the other game => not equal
            if p2 == None: 
                return None
            
            #Check position equality
            if p2.position  != p.position:
                return None
            
            #Check the layer of the pieces are equal 
            #(as some bugs may be on top of the hive)
            if p2.level != p.level:
                return None
            
        #If we reach this point the games are equal
        return True
            



def testHiveGameClass():
    
    
    #testGame = HiveGame('../Hive-games/2019/games-May-21-2019/HV-WeakBot-guest-2019-05-15-2238.sgf')
    #assert testGame.gameResult == 'black win'
    
    #Test that the different functions work as expected.
    gameName1 = '../Hive-games/2020/games-Jun-13-2020/T!HV-Frasco92-RoXar-2020-06-12-1659.sgf'
    gameName2 = '../Hive-games/2019/games-May-21-2019/T!HV-nevir-MaxShark-2019-05-20-2000.sgf'
    game1 = HiveGame(gameName1)
    game1a = HiveGame(gameName1)
    game2 = HiveGame(gameName2)
    
    assert not game1.isEqualTo(game2)
    assert not game1.toStandardPosition().isEqualTo(game2.toStandardPosition())
    
    #Load the same game twice
    game1 = HiveGame(gameName2)
    game2 = HiveGame(gameName2)
    assert game1.isEqualTo(game2) == True
    assert game1.toStandardPosition().toStandardPosition().isEqualTo(game2.toStandardPosition()) == True
    
    #Need to reset the games once modified
    game1 = HiveGame(gameName1)
    game2 = HiveGame(gameName2)
    
    #Test rotation and back again
    assert game1.rotGame60CCW().rotGame60CW().isEqualTo(game1a) == True
    
    game1 = HiveGame(gameName1)
    game1a = HiveGame(gameName1)
    assert game1.rotGame60CW().rotGame60CCW().isEqualTo(game1a) == True
    
    game1 = HiveGame(gameName1)
    game1a = HiveGame(gameName1)
    assert game1.rotGame60CW().rotGame60CW().isEqualTo(game1a.rotGame120CW()) == True
    
    game1 = HiveGame(gameName1)
    game1a = HiveGame(gameName1)
    assert game1.rotGame120CCW().rotGame120CW().isEqualTo(game1a) == True
    
    game1 = HiveGame(gameName1)
    game1a = HiveGame(gameName1)
    assert game1.reflGameXaxis().reflGameXaxis().isEqualTo(game1a) == True
    
    game1 = HiveGame(gameName1)
    game1a = HiveGame(gameName1)
    assert game1.rotGame180().rotGame180().isEqualTo(game1a) == True
    
    game1 = HiveGame(gameName1)
    game1a = HiveGame(gameName1)
    assert game1.rotGame180().rotGame60CW().rotGame120CW().isEqualTo(game1a) == True
    
    #Test transformation to standard position
    game1 = HiveGame(gameName1)
    game1a = HiveGame(gameName1)
    assert game1.toStandardPosition().isEqualTo(game1a.translateGameBy(Position(-1,0))) == True
    
    game1 = HiveGame(gameName1)
    game1a = HiveGame(gameName1)
    assert game1.isEqualTo(game1a) == True
    game1a.gameType = 'Hive-PL'
    assert not game1.toStandardPosition().isEqualTo(game1a.toStandardPosition())
    