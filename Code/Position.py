#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 25 14:06:56 2020

Class to handle coordinates in Hive according to how they are used in the 
entomology Hive position editor.
cf.
https://entomology.appspot.com/hive.html?bg=0&board=:w***@bA**@bB***@bG*@bL*@bM*@bP*@bQ**@bS***@wA**@wB***@wG*@wL*@wM*@wP*@wQ**@wS&grid=1

@author: epenjos
"""


class Position:
    
    def __init__(self, aA, aB):
        self.a = aA
        self.b = aB
    
    def importBSCoords(self, coordinates):
        #handle the conversion to numerical coordinates from the format 
        #used at BoardSpace
        # a,b are non-orhogonal coordinates of the hex-grid
        # N 13 = ( 0, 0)
        # N 12 = ( 0, 1)
        # O 13 = ( 1, 0)
        # M 11 = (-1, 2)
        # O 14 = ( 1,-1)
        # M 12 = (-1, 1)
        
        coords = coordinates.split()
        self.a = ord(coords[0]) - 78 #coords[1] the letter coordinate
        self.b = 13 - int(coords[1]) #coords[2] is the numerical coordinate
        return self
        
        
    #Overloading the '+' operator
    def __add__(self, other):
        newA = self.a + other.a
        newB = self.b + other.b
        return Position(newA,newB)
    
    def __sub__(self, other):
        newA = self.a - other.a
        newB = self.b - other.b
        return Position(newA,newB)
    
    #The scalar product for vectors implemented
    def __mul__(self, other):
        return self.a * other.a + self.b * other.b
    
    def __neg__(self):
        return Position(-self.a, -self.b)
        
    def __eq__(self, other):
        return (self.a == other.a) & (self.b == other.b)
    
    def __ne__(self, other):
        return not self.__eq__(other)
        
    
    #60 degrees rotation counter-clockwise transformation
    # e1 -> e1 - e2
    # e2 -> e1
    # [ 1 1 ] [a] 
    # [-1 0 ] [b]
    def rot60CCW(self):
        newA = Position( 1, 1)*self
        newB = Position(-1, 0)*self
        return Position(newA, newB)
    
    def rot120CCW(self):
        newA = Position( 0, 1)*self
        newB = Position(-1,-1)*self
        return Position(newA, newB)
    
    def rot180CCW(self):
        newA = Position(-1, 0)*self
        newB = Position( 0,-1)*self
        return Position(newA, newB)
        
    def rot60CW(self):
        newA = Position( 0,-1)*self
        newB = Position( 1, 1)*self
        return Position(newA, newB)
    
    def rot120CW(self):
        newA = Position(-1,-1)*self
        newB = Position( 1, 0)*self
        return Position(newA, newB)
    
    def reflXaxis(self):
        newA = Position( 1, 1)*self
        newB = Position( 0,-1)*self
        return Position(newA, newB)
        
        
        
    def __repr__(self):
        return "(%s,%s)" % (self.a, self.b)
    
    
def testPositionClass():
    inpStr = ["N 13",   "N 12",  "O 13",   "M 11",   "O 14",   "M 12"]
    expRes = ["(0,0)", "(0,1)", "(1,0)", "(-1,2)", "(1,-1)", "(-1,1)"]
    for i, val in enumerate(inpStr):
        if str(Position(0,0).importBSCoords(val)) != expRes[i]:
            print("Position conversion error:" + val + "=>" + str(Position(0,0).importBSCoords(val)))
        
    assert Position(2,1).reflXaxis() == Position(3,-1)
    assert Position(-4,2).reflXaxis() == Position(-2,-2)
    
    assert Position(2,1).rot60CCW() == Position(3,-2)
    assert Position(4,-1).rot60CCW() == Position(3,-4)
    
    assert Position(2,1).rot60CW() == Position(-1,3)
    assert Position(7,-4).rot60CW() == Position(4,3)
    
    assert Position(2,1).rot120CW() == Position(-3,2)
    assert Position(-2,-2).rot120CW() == Position(4,-2)