#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 18 10:32:05 2020

@author: epenjos
"""
from Position import Position



class Piece : 
    def __init__(self, aName, aColor, aCoordinates, aLevel):
        self.name = aName # will be e.g., "wA1"
        self.color = aColor # white or black
        self.level = aLevel #the height over the hive, ground level is zero
        self.position = Position(0,0).importBSCoords(aCoordinates)
        
        
    def moveTo(self, newCoordinates):
        self.position = Position(0,0).importBSCoords(newCoordinates)

    def isSamePieceAtSamePosAs(self, other):
        return (self.name == other.name) & (self.position == other.position)
    
    def getEntString(self):
        if self.position.a >= 0: 
            strA = '+' + str(self.position.a)
        else: 
            strA = str(self.position.a)
        if self.position.b >= 0: 
            strB = '+' + str(self.position.b)
        else: 
            strB = str(self.position.b)
        
        return self.name + strA + strB
        
        
    def __repr__(self):
        return "<%s @%s>" % (self.name, self.position)
        # neighborString = ""
        # for n in self.neighbors:
        #     neighborString = neighborString + n + ':' + self.neighbors[n].name + ', '
        
        # return "<Piece: %s at: %s, neighbors: %s>" % (self.name, self.coordinates, neighborString)
        
        
    
        
        