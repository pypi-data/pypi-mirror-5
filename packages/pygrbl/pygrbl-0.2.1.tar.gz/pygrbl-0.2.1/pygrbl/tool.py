#!/usr/bin/env python
# tool.py : Parses a gcode file
# [2012.07.31] Mendez

# [System]
import re
import sys
import math
from pprint import pprint
from string import Template
from copy import deepcopy

# [Installed]
from clint.textui import colored, puts, indent, progress

# [Package]
from pygrbl import util, mill
# from util import error, distance
# from mill import Mill

# [Constants]
AXIS='XYZ'

TEMPLATE='''(Built with python and a dash of Mendez)
(GCODE Start nCommands:${ncommand} npaths:${nmill})
${units}
${movement}
${gcode}
(GCODE End)
${footer}'''





def nan():
  return [float('nan')]*3
def origin():
  return [0.0]*3

# Moves and the sort
def noop(self,m=None,t=None):
  pass
def home(self,m=None,t=None):
  self.append(origin()+[0]) #origin
def inch(self,m=None,t=None):
  self.units = 'inch'
def mm(self,m=None,t=None):
  self.unis = 'mm'
def absolute(self,m=None,t=None):
  self.abs = True
def relative(self,m=None,t=None):
  self.abs = False
def move(self,m,t):
  '''Moves to location. if NaN, use previous. handles rel/abs'''
  
  loc = convert(self,m) # ensure everything is in inches
  loc = [x if not math.isnan(x) else self[-1][i] for i,x in enumerate(loc)] # clean NAN
  if not self.abs: loc += self[-1][:] # rel/abs
  loc.append(t)
  self.append(loc)
def convert(self,m):
  if self.units == 'mm':
    m = [x*25.4 for x in m]
  return m
def millMove(self, next, height):
  '''Move the toolbit to the next mill location'''
  last = self[-1]
  move(self, last[0:2]+[height], 0) # lift off of board
  move(self, next[0:2]+[height], 0) # Move to next pos


GCMD = {0:  move,
        1:  move,
        4:  noop,
        20: inch,
        21: mm,
        90: absolute,
        91: relative}



class Tool(list):
  def __init__(self,gcode=None):
    ''' By default the machine starts in absolute with "mm" as the units.
    Go to the home location and then add moves'''
    self.abs = True
    self.units = 'inch'
    self.mills = []
    home(self)
    
    if gcode:
      self.build(gcode)
  
  
  def __repr__(self):
    return '%s() : %i locations, units: %s'%(self.__class__.__name__, len(self),self.units)
  
  def build(self,gcode):
    '''Parse gCode listing to follow a bit location'''
    puts(colored.blue('Building Toolpath:'))
    
    # for each line of the gcode, accumulate the location of a toolbit
    for i,line in enumerate(progress.bar(gcode)):
    # for i,line in enumerate(gcode):
      move = nan()
      if 'G' in line:
        t = line['G']  # type of command
        for j,x in enumerate(AXIS): # grab all changes
          if x in line: move[j] = line[x]
        
        # Apply changes to the object
        try:
          fcn = GCMD[t]
          fcn(self,move,t)
        except KeyError:
          error('Missing command in GCMD: %d'%(t))
  
  def length(self):
    '''get the length of a toolpath'''
    length = 0.0
    for i in range(len(self)-1):
      length += distance(self[i],self[i+1])
    return length
  
  def uniq(self):
    '''make the toolpath uniq'''
    for i in reversed(range(1,len(self))):
      if self[i] == self[i-1]:
        self.pop(i)
    
  
  def millLength(self):
    '''Gets the length of the self.mills part'''
    length = 0.0
    for mill in self.mills:
      length += mill.length()
    return length
  
  def groupMills(self):
    '''Groups the toolpath into individual mills'''
    puts(colored.blue('Grouping paths:'))
    
    mill = Mill();
    for x,y,z,t in progress.bar(self):
    # for i,[x,y,z,t]  in enumerate(self):
      if t == 1:
        mill.append([x,y,z])
      else:
        if len(mill) > 0:
          self.mills.append(mill)
          mill = Mill() # ready for more mills
  
  
  
  def uniqMills(self):
    '''Uniqify the points in each of the millings'''
    for mill in self.mills:
      mill.uniqify()
  
  def setMillHeight(self, millHeight=None, drillDepth=None):
    '''Sets the Mill height, for spot drilling
        millHeight and drillHeight in MILs'''
    for mill in self.mills:
      if mill.isDrill():
        mill.setZ(drillDepth/1000.)
      else:
        mill.setZ(millHeight/1000.)
  
  def getNextMill(self, X):
    '''Gets the next next mill to point X, using just the mill start point.'''
    distances = [distance(mill[0],X) for mill in self.mills]
    index = distances.index(min(distances))
    # print '%i : % 4.0f mil'%(index, min(distances)*1000.0)
    return self.mills.pop(index)
  
  def getClosestMill(self, X):
    ''' Improved getNextMill, optimizes the location to start in the mill 
    Now checks to see if the starting and ending point are close so can be 
    reordered.  This ends up being a traveling salesman problem, so 
    keeping with this solution is easiest. '''
    # get the path with a point that is closest to X
    distances = [distance(mill.closestLocation(X),X) for mill in self.mills]
    index = distances.index(min(distances))
    mill = self.mills.pop(index)
    # print '%i : % 4.0f mil'%(index, min(distances)*1000.0)
    
    # reorder the path so that the start is close to x
    mill.reorderLocations(X)
    return mill
  
  
  def reTool(self, moveHeight=None):
    '''Rebuild the toolpath using the Mills
    moveHeight is in MILLs and is the height at which the machine moves'''
    # self[:] = list() # Remove old toolpath !!!
    while len(self)>0: self.pop()
    home(self)
    self.abs=True
    self.units='inch'
    
    heightInches = moveHeight/1000.
    
    for mill in self.mills:
      millMove(self, mill[0], heightInches)
      for x in mill:
        move(self, x, 1) # mill each location
    millMove(self, origin(), heightInches)
  
  
  def buildGcode(self):
    '''This returns a string with the GCODE in it.'''
    lines = []
    iMill = 1
    for i,[x,y,z,t] in enumerate(self):
      if ([l[3] for l in self[i-1:i+2]] == [0,0,1]):
        lines.append('\n(Mill: %04i)'%(iMill))
        iMill += 1
      lines.append('G%02i   X%.3f Y%.3f Z%.3f'%(t,x,y,z))
    gcode ='\n'.join(lines)
    params = dict(units='G20' if (self.units == 'inch') else 'G21',
                  movement='G90' if self.abs else 'G91',
                  gcode=gcode,
                  nmill=iMill,
                  ncommand=len(self),
                  footer='')
    return Template(TEMPLATE).substitute(params)



    