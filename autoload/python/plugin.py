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
vim.command('sign define %s text=BP texthl=Search'%(VBP_NAME)) #linehl=Search

# print("Full path: "+str(vim.eval("echo('%:p')")))
global ctrl
ctrl = None

def cerr(data):
	sys.stderr.write(data)

def BufferLoadLa():
	path = vim.eval('expand("%:p")')
	if not os.path.exists(path):
		return
	signlist = {}
	import re
	rex = re.compile(r'line=(\d+)\s+id=(\d+)\s+name=(\S+)', re.MULTILINE)
	text = vim.eval('SDebugSignlistCurrent()')
	if not text:
		sys.stderr.write("no signs to load")
		return
	for match in rex.finditer(text):
		line, id, name = match.groups()
		if name == VBP_NAME:
			signlist[line] = True

	# Attempt to load breakpoint signs into this file
	# Duplicate breakpoint signs are ignored
	for src,lines in model_bp.Model.container.iteritems():
		if path != src and os.path.basename(path) != src:
			continue
		if os.path.basename(path) == src:
			src = path
		for line,bp in lines.iteritems():
			if str(line) in signlist:
				continue
			vim.command('sign place %i line=%i name=%s file=%s'%(line,line,VBP_NAME,path))
	pass


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
		view_bt.View.reset_cursor()
		BacktraceNavigate()
	elif state == "running":
		print(state)
		view_bt.View.clear()
	elif state == "stepping":
		print(state)
		view_bt.View.render(model_bt.Model)
		view_bt.View.reset_cursor()
		BacktraceNavigate()
	elif state == "crashed":
		print(state)
		view_bt.View.render(model_bt.Model)
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
	if not view_bt.View.valid(): return

	# Get object at current line, can be frame - but can also be thread fold
	frame = view_bt.View.info(model_bt.Model)
	if not frame:
		Refresh(ctrl.timeoutEvents)
		return

	# Attempt to navigate to frame
	if isinstance(frame, model_bt.Frame):
		# Change frame, update the view
		changed = ctrl.select_frame(frame)
		view_bt.View.render(model_bt.Model)

		# Open and render frame source, refresh the controller
		_view = view_src.View
		if not _view.valid():
			print("error opening frame; source window undefined")
			return
		_view.link.tab.switch()
		_view.link.tab.window.switch()
		_view.render(model_src.Model)
		# Refresh(ctrl.timeoutEventsFast)
	else:
		model_bt.Model.fold(frame.id)
		model_bt.Model.navigated = frame.number
		view_bt.View.render(model_bt.Model)
		view_bt.View.link.switch_to()

# Create breakpoint
# Supply source/line, or leave blank to create breakpoint under cursor
def BreakpointToggle(source='', line=''):
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
			vim.command('sign place %i line=%i name=%s file=%s'%(line,line,VBP_NAME,source))
		except vim.error as err:
			print err
		print("added breakpoint in %s line %i"%(source,line))
	else:
		if ctrl.running(): ctrl.breakpoint_delete(bp.source, bp.line)
		model_bp.Model.delete(bp.source, bp.line)
		vim.command('sign unplace %i file=%s'%(line,source))
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


