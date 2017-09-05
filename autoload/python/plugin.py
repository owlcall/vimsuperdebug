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

import controller_lldb
import view_backtrace
import model_breakpoints
import vim

global controller
controller = None

def Launch():
	global controller
	controller = controller_lldb.Controller()

	# if debug tab does not exist - open new tab
	# split vertical for variables
	# split right horizontally for program output
	# split left horizontally for backtrace

	# When opening new buffers, windows and tabs - add appropriate automated
	# callbacks to deinitialize the view component


def Run(program, args=[]):
	global controller
	controller.run(program, args)

def Quit():
	global controller
	controller.quit()

def OpenViewBacktrace():
	global controller
	view = view_backtrace.View
	if not view.valid():
		vim.command(":enew")
		vim.command(":silent file [BACKTRACE]")
		vim.command(":map <silent> <buffer> <Enter> : python BacktraceNavigate()<CR>")
		view.initialize()
		view.link.tab.window.buffer.set_readonly(True)
		view.link.tab.window.buffer.set_nofile(True)
	else:
		# View exists; Simply open view's buffer here
		vim.command(":b"+str(view.link.tab.window.buffer.vim.number))

def OpenViewSource():
	global controller
	view = view_source.View
	if not view.valid():
		vim.initialize()
	else:
		vim.command(":"+str(vim.link.tab.window.vim.number)+' wincmd w')

def OpenViewVariables():
	global controller
	pass

def OpenViewConsole():
	global controller
	pass

def BacktraceNavigate():
	global controller
	view = view_backtrace.View
	if not view.valid():
		return
	frame = view.info()
	if not controller.select_frame(frame):
		return

	# First update the backtrace
	controller.backtrace()
	view.render()

	# Now open the source as appropriate for the frame
	view = view_source.View
	if not view.valid():
		print("error source window undefined")
		return
	view.link.tab.switch()
	view.link.tab.window.switch()
	view.render()

def Breakpoint(source, line):
	breakpoints = model_breakpoints.Breakpoint
	breakpoints.add(source, line)

	global controller
	if controller.running():
		controller.breakpoint(source, line)

def BreakpointsClear():
	global controller
	controller.breakpoints_clear()

	breakpoints = model_breakpoints.Breakpoint
	for _,item in breakpoints.container.iteritems():
		item.set = False

def Pause():
	global controller
	controller.pause()

def Resume():
	global controller
	controller.resume()

def StepOver():
	global controller
	controller.step_over()

def StepInto():
	global controller
	controller.step_into()

def StepOut():
	global controller
	controller.step_out()

def Attach(pid=-1, name=""):
	global controller
	controller(pid, name)

def Detach():
	global controller
	controller.detach()


