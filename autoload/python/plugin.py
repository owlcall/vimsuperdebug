#!/usr/bin/env python
#
# plugin.py 
# Copyright (c) 2017 owl
#

# Enable module loading from current directory
import os, sys, inspect
directory = os.path.dirname(inspect.getfile(inspect.currentframe()))
sys.path.append(directory)

import model.backtrace as model_bt
import model.breakpoint as model_bp
import model.source as model_src
import vim
import view.backtrace as view_bt
import view.breakpoint as view_bp
import view.source as view_src
import controller.lldbc

ctrl = None
view_bp.View.initialize()

class Debugger:
	# self.ctrl = None
	def launch(args):
		# self.ctrl 
		pass

def cerr(data):
	sys.stderr.write(data)

def BufferLoad():
	view_bp.View.update_current(model_bp.Model)

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
def Refresh(timeout=0, nesting=0):
	global ctrl
	if not ctrl: return
	if nesting > 2: return

	state = ctrl.refresh(timeout)
	if state == "invalid":
		# Invalid state needs to be ignored, nothing changes - and no
		# operation should be allowed
		pass
	elif state == "unloaded":
		print(state)
	elif state == "connected":
		print(state)
	elif state == "attaching":
		print(state)
	elif state == "launching":
		print(state)
	elif state == "stopped":
		# print(state)
		view_bt.View.render()
		view_bt.View.reset_cursor()
		#FIXME: Only navigate if the source/line has changed
		BacktraceNavigate()
	elif state == "running":
		print(state)
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
		print(state)
	elif state == "exited":
		model_bt.Model.clear()
		view_bt.View.clear()
		print(state)
	elif state == "suspended":
		print(state)

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
	if not ctrl: return

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
		source,line,modified = view_bp.View.line_info()
		if modified:
			cerr("error setting breakpoint; buffer has unsaved changes.")
			return
		if not source:
			print("error setting breakpoint; anonymous buffer.")
			return

	# Retrieve the breakpoint based on source/line
	# Some breakpoints can contain just filenames - this is our fallback
	bp = model_bp.Model.get(source, line)
	if not bp: bp = model_bp.Model.get(os.path.basename(source),line)
	if not bp:
		model_bp.Model.add(source, line)
		view_bp.View.add(source, line)
		if ctrl and ctrl.running(): ctrl.breakpoint_add(source, line)
		print("added breakpoint from %s line %i"%(source,line))
	else:
		if ctrl and ctrl.running(): ctrl.breakpoint_delete(bp.source, bp.line)
		view_bp.View.remove(source, line)
		model_bp.Model.delete(bp.source, bp.line)
		print("deleted breakpoint from %s line %i"%(source,line))

def BreakpointsClear():
	global ctrl
	ctrl.breakpoints_clear()
	for _,item in model_bp.Model.container.iteritems():
		item.set = False
	view_bp.View.clear()

def Pause():
	global ctrl
	ctrl.pause()
	Refresh(ctrl.timeoutEventsFast)

def Continue():
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


