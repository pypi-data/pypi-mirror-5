#!/usr/bin/env python
# gcode.py : Parses a gcode file
# [2012.07.31] Mendez

# [System]
import re
import sys
from pprint import pprint

# [Installed]
from clint.textui import colored, puts, indent, progress

# [Package]


# [Constants]
CMDS = 'GXYZMP' # all of the basic letter commands



class GCode(list):
  def __init__(self, gcode):
    '''start with a gcode ascii file'''
    if isinstance(gcode, str):
      with open(gcode,'r') as f:
        lines = f.readlines()
        filename = gcode
    else:
      filename = gcode.name
      lines = gcode.readlines()
      gcode.close()
    self.filename = filename
    self.lines = lines
    self.ready = False
  
  def append(self,item):
    '''add the next nice to the object'''
    if self.ready : self.ready = False
    super(GCode, self).append(item)
  
  def parse(self):
    ''' convert the readlines into a parsed set of commands and values'''
    puts(colored.blue('Parsing gCode'))
    
    comment = r'\(.*?\)'
    whitespace = r'\s'
    command = r''.join([r'(?P<%s>%s(?P<%snum>-?\d+(?P<%sdecimal>\.?)\d*))?'%(c,c,c,c) for c in CMDS])
    for i,line in enumerate(progress.bar(self.lines)):
      l = line.strip()
      
      # find comments, save them, and then remove them
      m = re.findall(comment,l)
      l = re.sub(whitespace+'|'+comment,'',l).strip().upper()

      # Grab the commands
      c = re.match(command,l)
      
      # output commands to a nice array
      out = {}
      for cmd in CMDS:
        if c.group(cmd):
          # either a float if '.' or a int
          fcn = float if c.group(cmd+'decimal') else int
          out[cmd] = fcn(c.group(cmd+'num'))
          out['index'] = i
      
      # if we have some commands save them
      if len(out) > 0:
        self.append(out)
      
      