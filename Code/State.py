# -*- coding: utf-8 -*-
"""
Created on Mon Jun 29 20:08:37 2020

A state (or pattern) is defined as a game state and is a collection of pieces in a 
formation may include pieces specified by position, color, and type 
and may include wildcard pieces specified by position and only color or type.
A state object is used to check if a Hive game passes through a state or not,
and used for matching games against states.

A state may be defined by writing a string specifying it, most easily taken
from the URL of the game drawn in the Entomology position editor, or be taken 
from a game opening, in the latter case the individual pieces may be changed 
to become wildcard pieces.

In matching games with a state use:
    aState = State().stateFromString('bQ+1-2wQ+0+0b*+1-1')
    aGame  = HiveGame(path)
    if aGame.passesByState(aState) == True :
        #a match
    

@author: jonas
"""


class State :
    pass


