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

global controller

def Launch():
	controller = contoller_lldb.Controller()

def Run(program, args=[]):
	controller.run(program, args)

def Quit():
	controller.quit()

def NavBacktrace():
	# controller.
	pass

def SetBreakpoint(source, line):
	# controller.
	pass

def Pause():
	controller.pause()

def Resume():
	controller.resume()

def StepOver():
	controller.step_over()

def StepInto():
	controller.step_into()

def StepOut():
	controller.step_out()

def Attach(pid=-1, name=""):
	controller(pid, name)

def Detach():
	controller.detach()


