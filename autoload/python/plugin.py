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
import view_source
import model_breakpoints
import model_source
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

def Refresh(timeout=0):
	global controller
	state = controller.refresh(timeout)
	if state == "invalid":
		# print("invalid")
		pass
	elif state == "unloaded":
		print("unloaded")
	elif state == "connected":
		print("connected")
	elif state == "attaching":
		print("attaching")
	elif state == "launching":
		print("launching")
	elif state == "stopped":
		view_backtrace.View.render()
		BacktraceNavigate()
	elif state == "running":
		print("running")
	elif state == "stepping":
		view_backtrace.View.render()
		BacktraceNavigate()
	elif state == "crashed":
		view_backtrace.View.render()
		BacktraceNavigate()
	elif state == "detached":
		print("detached")
	elif state == "exited":
		print("exited")
	elif state == "suspended":
		print("suspended")

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
		vim.command(":enew")
		view.initialize()
		view.link.tab.window.buffer.set_nofile(True)
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
	if not view.valid(): return

	frame = view.info()
	controller.select_frame(frame)
	# if not controller.select_frame(frame):
		# print("frame not changed")
		# return

	#TODO: Check if frame changed

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
	Refresh(controller.timeoutEventsFast)

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
	Refresh(controller.timeoutEventsFast)

def Resume():
	global controller
	controller.resume()
	Refresh()

def StepOver():
	global controller
	controller.step_over()
	Refresh(controller.timeoutEventsFast)

def StepInto():
	global controller
	controller.step_into()
	Refresh(controller.timeoutEventsFast)

def StepOut():
	global controller
	controller.step_out()
	Refresh(controller.timeoutEventsFast)

def Attach(pid=-1, name=""):
	global controller
	controller(pid, name)
	Refresh()

def Detach():
	global controller
	controller.detach()
	Refresh()


