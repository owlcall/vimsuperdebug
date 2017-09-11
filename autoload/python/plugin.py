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

VBP_NAME = "sdebug_bp"
vim.command('silent sign define %s text=BP texthl=Search'%(VBP_NAME)) #linehl=Search

# print("Full path: "+str(vim.eval("echo('%:p')")))
global ctrl
ctrl = None

def cerr(data):
	sys.stderr.write(data)

def BufferLoad():
	import re
	# Ensure the expanded buffer path is valid/exists
	path = vim.eval('expand("%:p")')
	if not os.path.exists(path): return

	# Parse existing signs to ensure we don't add duplicates
	rex = re.compile(r'line=(\d+)\s+id=(\d+)\s+name=(\S+)', re.MULTILINE)
	text = vim.eval('SDebugSignlistCurrent()')
	if not text:
		cerr("no signs to load")
		return
	signlist = {}
	for match in rex.finditer(text):
		line, id, name = match.groups()
		if name == VBP_NAME:
			signlist[line] = True

	# Attempt to load breakpoint signs into this file
	# Duplicate breakpoint signs are ignored
	for src,lines in model_bp.Model.container.iteritems():
		if os.path.basename(path) != src and src != path: continue
		if os.path.basename(path) == src: src = path
		# Update each breakpoint line in current file as a BP sign
		for ln, bp in lines.iteritems():
			if str(ln) in signlist: continue
			# Must provide full path file as argument, otherwise errors
			vim.command('silent sign place %i line=%i name=%s file=%s'%(ln,ln,VBP_NAME,path))

# Initialize debugger and bootstrap the controller
def Launch():
	global ctrl
	ctrl = controller.lldbc.Controller()

# Run the program being debugged
def Run(program, args=[]):
	global ctrl
	ctrl.run(program, args)

# Quit debug controller (and associated process)
def Quit():
	global ctrl
	ctrl.quit()

# Refresh debugger state
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
		print(state)
		view_bt.View.render()
		view_bt.View.reset_cursor()
		BacktraceNavigate()
	elif state == "running":
		# print(state)
		view_bt.View.clear()
	elif state == "stepping":
		print(state)
		view_bt.View.render()
		view_bt.View.reset_cursor()
		BacktraceNavigate()
	elif state == "crashed":
		print(state)
		view_bt.View.render()
		view_bt.View.reset_cursor()
		BacktraceNavigate()
	elif state == "detached":
		print("detached")
	elif state == "exited":
		model_bt.Model.clear()
		view_bt.View.clear()
		print("exited")
	elif state == "suspended":
		print("suspended")

# Initilize/select backtrace view
def OpenViewBacktrace():
	if not view_bt.View.valid():
		view_bt.View.initialize(model_bt.Model)
	else:
		view_bt.View.switch_to()

# Initilize/select source view
def OpenViewSource():
	if not view_src.View.valid():
		view_src.View.initialize(model_src.Model)
	else:
		view_src.View.switch_to_window()

def OpenViewVariables():
	global ctrl
	pass

def OpenViewConsole():
	global ctrl
	pass

# Open frame under cursor in backtrace view
def BacktraceNavigate():
	global ctrl
	# Get line selection from the backtrace view
	frame = view_bt.View.info()
	if not frame:
		Refresh(ctrl.timeoutEvents)
		return

	if isinstance(frame, model_bt.Frame):
		# Switch frames to the one under cursor
		changed = ctrl.select_frame(frame)

		# Update backtrace/source models and views
		ctrl.update_source()
		view_bt.View.render()
		view_src.View.render()
	else:
		# Attempt to fold the thread
		model_bt.Model.fold(frame.id)
		model_bt.Model.navigated = frame.number
		view_bt.View.render()

# Toggle breakpoint
def BreakpointToggle(source='', line=''):
	global ctrl
	# Detect source/line if necessary from current buffer/window
	if not source or not line:
		source = vim.eval("expand('%:p')")
		line = vim.current.window.cursor[0]
		# Disable ability to set breakpoints on modified files
		if vim.current.buffer.options['modified']:
			cerr("error setting breakpoint; buffer has unsaved changes.")
			return

	# Retrieve the breakpoint based on source/line
	# Some breakpoints can contain just filenames - this is our fallback
	bp = model_bp.Model.get(source, line)
	if not bp:
		bp = model_bp.Model.get(os.path.basename(source),line)

	if not bp:
		model_bp.Model.add(source, line)
		if ctrl.running(): ctrl.breakpoint(source, line)
		try:
			vim.command('silent sign place %i line=%i name=%s file=%s'%(line,line,VBP_NAME,source))
		except vim.error as err:
			print err
		print("added breakpoint in %s line %i"%(source,line))
	else:
		if ctrl.running(): ctrl.breakpoint_delete(bp.source, bp.line)
		model_bp.Model.delete(bp.source, bp.line)
		vim.command('silent sign unplace %i file=%s'%(line,source))
		print("deleted breakpoint from %s line %i"%(source,line))

def BreakpointsClear():
	global ctrl
	ctrl.breakpoints_clear()

	for _,item in model_bp.Model.container.iteritems():
		item.set = False
	#TODO: delete signs for our breakpoints


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
	ctrl.update_source()
	view_src.View.render()

def StepInto():
	global ctrl
	ctrl.step_into()
	Refresh(ctrl.timeoutEventsFast)
	ctrl.update_source()
	view_src.View.render()

def StepOut():
	global ctrl
	ctrl.step_out()
	Refresh(ctrl.timeoutEventsFast)
	ctrl.update_source()
	view_src.View.render()

def Attach(pid=-1, name=""):
	global ctrl
	ctrl.attach(pid, name)
	Refresh()

def Detach():
	global ctrl
	ctrl.detach()
	Refresh()


