#!/usr/bin/env python
#
# plugin.py 
# Copyright (c) 2017 owl
#

# Enable module loading from current directory
import os
import inspect
import sys
directory = os.path.dirname(inspect.getfile(inspect.currentframe()))
sys.path.append(directory)

import import_lldb
import controller_lldb

def Launch():
	pass

def Run():
	pass

def Quit():
	pass

def NavBacktrace():
	pass

def SetBreakpoint(source, line):
	pass

def Pause():
	pass

def Resume():
	pass

def StepOver():
	pass

def StepInto():
	pass

def StepOut():
	pass

def Detach():
	pass
