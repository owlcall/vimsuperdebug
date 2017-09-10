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

import vim

import model.backtrace as model_bt
import model.breakpoint as model_bp
import model.source as model_src

import view.backtrace as view_bt
#import view.breakpoint as view_bp
import view.source as view_src

import controller.lldbc

# print("Full path: "+str(vim.eval("echo('%:p')")))
global ctrl
ctrl = None

def Launch():
	global ctrl
	ctrl = controller.lldbc.Controller()

	# if debug tab does not exist - open new tab
	# split vertical for variables
	# split right horizontally for program output
	# split left horizontally for backtrace

	# When opening new buffers, windows and tabs - add appropriate automated
	# callbacks to deinitialize the view component


def Run(program, args=[]):
	global ctrl
	ctrl.run(program, args)

def Quit():
	global ctrl
	ctrl.quit()

def Refresh(timeout=0):
	global ctrl
	state = ctrl.refresh(timeout)
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
		view_bt.View.render(model_bt.Model)
		BacktraceNavigate()
	elif state == "running":
		print("running")
	elif state == "stepping":
		view_bt.View.render(model_bt.Model)
		BacktraceNavigate()
	elif state == "crashed":
		view_bt.View.render(model_bt.Model)
		BacktraceNavigate()
	elif state == "detached":
		print("detached")
	elif state == "exited":
		print("exited")
	elif state == "suspended":
		print("suspended")

def OpenViewBacktrace():
	global ctrl
	_view = view_bt.View
	if not _view.valid():
		vim.command(":enew")
		vim.command(":silent file [BACKTRACE]")
		vim.command(":map <silent> <buffer> <Enter> : python BacktraceNavigate()<CR>")
		_view.initialize()
		_view.link.tab.window.buffer.set_readonly(True)
		_view.link.tab.window.buffer.set_nofile(True)
	else:
		# View exists; Simply open view's buffer here
		vim.command(":b"+str(_view.link.tab.window.buffer.vim.number))

def OpenViewSource():
	global ctrl
	_view = view_src.View
	if not _view.valid():
		vim.command(":enew")
		_view.initialize()
		_view.link.tab.window.buffer.set_nofile(True)
	else:
		vim.command(":"+str(_view.link.tab.window.vim.number)+' wincmd w')
	vim.command(":map <silent> <Leader>o : python StepOut()<CR>")
	vim.command(":map <silent> <Leader>i : python StepInto()<CR>")
	vim.command(":map <silent> <Leader>n : python StepOver()<CR>")

def OpenViewVariables():
	global ctrl
	pass

def OpenViewConsole():
	global ctrl
	pass

def BacktraceNavigate():
	global ctrl
	if not view_bt.View.valid(): return

	frame = view_bt.View.info(model_bt.Model)
	changed = ctrl.select_frame(frame)

	# First update the backtrace
	#TODO: if changed and view is empty - render
	view_bt.View.render(model_bt.Model)

	# Now open the source as appropriate for the frame
	_view = view_src.View
	if not _view.valid():
		print("error source window undefined")
		return
	_view.link.tab.switch()
	_view.link.tab.window.switch()
	_view.render(model_src.Model)
	Refresh(ctrl.timeoutEventsFast)
	view_bt.View.link.switch_to()

# Create breakpoint
# Supply source/line, or leave blank to create breakpoint under cursor
def BreakpointToggle(source='', line=''):
	for _ in vim.current.buffer.options:
		print(_)
	print(vim.current.buffer)
	if not source or not line:
		source = vim.current.buffer.name
		line = vim.current.window.cursor[0]
		print("AUTO: "+str(source)+":"+str(line))

		if modified:
			controller.lldbc.cerr("can't set breakpoint on modified buffer. Please save your changes")

	global ctrl
	bp = model_bp.Model.get(source, line)
	if not bp:
		model_bp.Model.add(source, line)
		if ctrl.running(): ctrl.breakpoint(source, line)
	else:
		model_bp.Model.delete(source, line)
		if ctrl.running(): ctrl.breakpoint(source, line)
		#TODO: here we need to clear this breakpoint from any active files

def BreakpointsClear():
	global ctrl
	ctrl.breakpoints_clear()

	for _,item in model_bp.Model.container.iteritems():
		item.set = False

def Pause():
	global ctrl
	ctrl.pause()
	Refresh(ctrl.timeoutEventsFast)

def Resume():
	global ctrl
	ctrl.resume()
	Refresh()

def StepOver():
	global ctrl
	ctrl.step_over()
	Refresh(ctrl.timeoutEventsFast)

def StepInto():
	global ctrl
	ctrl.step_into()
	Refresh(ctrl.timeoutEventsFast)

def StepOut():
	global ctrl
	ctrl.step_out()
	Refresh(ctrl.timeoutEventsFast)

def Attach(pid=-1, name=""):
	global ctrl
	ctrl.attach(pid, name)
	Refresh()

def Detach():
	global ctrl
	ctrl.detach()
	Refresh()


