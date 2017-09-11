#!/usr/bin/env python
#
# controller_lldb.py 
# Copyright (c) 2017 owl
#

# Import models which are changed by the controller
# from python.model.backtrace import Thread
# from model_backtrace import Model as model_bt.Model
# from model_breakpoints import Breakpoint as Breakpoints
# from model_source import Model as model_src.Model

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import import_lldb, lldb

import model.backtrace as model_bt
import model.breakpoint as model_bp
import model.source as model_src

def cerr(data):
	sys.stderr.write(data)

def state_type_to_str(enum):
	"""Returns the stateType string given an enum."""
	if enum == lldb.eStateInvalid:
		return "invalid"
	elif enum == lldb.eStateUnloaded:
		return "unloaded"
	elif enum == lldb.eStateConnected:
		return "connected"
	elif enum == lldb.eStateAttaching:
		return "attaching"
	elif enum == lldb.eStateLaunching:
		return "launching"
	elif enum == lldb.eStateStopped:
		return "stopped"
	elif enum == lldb.eStateRunning:
		return "running"
	elif enum == lldb.eStateStepping:
		return "stepping"
	elif enum == lldb.eStateCrashed:
		return "crashed"
	elif enum == lldb.eStateDetached:
		return "detached"
	elif enum == lldb.eStateExited:
		return "exited"
	elif enum == lldb.eStateSuspended:
		return "suspended"
	else:
		return "uknown"

class Controller:
	def __init__(self):
		self.dbg = lldb.SBDebugger.Create()
		self.commander = self.dbg.GetCommandInterpreter()
		self.target = None
		self.process = None

		self.pid = -1
		self.proc_listener = None
		self.timeoutEvents = 1		# Number of seconds we wait for events
		self.timeoutEventsFast = 2	# Events which are expected to return fast end up waiting the longest (to avoid multple calls to refresh)

		self.operation = ""

	def running(self):
		return self.process != None

	def run(self, program, args=[]):
		error = lldb.SBError()
		info = lldb.SBLaunchInfo(args)

		if not self.dbg:
			cerr("error creating target \"%s\"; not initialized."%(program))
			return

		# Prevent lldb from crashing by trying to load python files from within dSYM
		result = lldb.SBCommandReturnObject()
		self.commander.HandleCommand("settings set target.load-script-from-symbol-file false", result)

		# Create new target (args are supplied when launching)
		# self.target = self.dbg.CreateTarget(program)
		self.target = self.dbg.CreateTarget(program, None, None, True, error)
		if not self.target or not error.Success():
			cerr("error creating target \"%s\". %s"%(program, str(error)))
			return
		
		# Initialize all the breakpoints
		for _, group in model_bp.Model.container.iteritems():
			for _, item in group.iteritems():
				self.breakpoint(item.source, item.line)

		# Launch target process
		self.process = self.target.Launch(info, error)
		if not self.process or not error.Success():
			cerr("error launching process \"%s\". %s"%(program, str(error)))
			return

		self.pid = self.process.GetProcessID()
		self.proc_listener = lldb.SBListener("proc_listener")
		self.process.GetBroadcaster().AddListener(self.proc_listener, lldb.SBProcess.eBroadcastBitStateChanged)

	def attach(self, pid=-1, pname=""):
		if not pid and not pname:
			cerr("error attaching; nothing to attach to.")
			return
		if self.process:
			cerr("error attaching to process \"%s\"; already attached."%(pname if pname else str(pid)))
			return

		error = lldb.SBError()
		self.target = self.dbg.CreateTarget('')
		self.proc_listener = lldb.SBListener("proc_listener")
		if pid:
			self.process = self.target.AttachToProcessWithID(self.proc_listener, pid, error)
		elif pname:
			self.process = self.target.AttachToProcessWithName(self.proc_listener, pname, False, error)
		if not error.Success():
			cerr("error attaching to process \"%s\". %s" %(program if program else str(pid), str(error)))
			return

	def quit(self):
		self.dbg.Terminate()
		self.target = None
		self.process = None
		self.proc_listener = None
		self.pid = -1
		model_bp.Model.unset_all()

	def pause(self, program):
		if not self.process:
			cerr("error pausing; no running process.")
			return
		self.process.Stop()

	def resume(self):
		if not self.process:
			cerr("error resuming; no running process.")
			return
		self.process.Continue()

	def backtrace(self):
		if not self.process:
			cerr("error getting backtrace; no running process.")
			return

		model_bt.Model.clear()
		threadSelected = self.process.GetSelectedThread() 
		frameSelected = threadSelected.GetSelectedFrame()
		thread_ids = []
		for _thread in self.process:
			thread = model_bt.Model.thread()
			thread.default = True if threadSelected == _thread else False
			thread.number = _thread.GetIndexID()
			thread.id = _thread.GetThreadID()
			if thread.default:
				model_bt.Model.selected = thread
				if thread.id not in model_bt.Model.expanded:
					model_bt.Model.fold(thread.id)
			thread_ids.append(_thread.GetThreadID())

			for _frame in _thread:
				frame = thread.frame()
				frame.default = True if thread.default and frameSelected.GetFrameID() == _frame.GetFrameID() else False
				frame.number = _frame.GetFrameID()
				frame.module = _frame.GetModule().GetFileSpec().GetFilename()

				if frame.default:
					thread.selected = frame

				function = _frame.GetDisplayFunctionName()
				frame.path = _frame.GetLineEntry().GetFileSpec().GetFilename()
				if function and _frame.GetLineEntry().GetFileSpec().GetDirectory():
					frame.name = _frame.GetFunctionName()
					frame.file = _frame.GetLineEntry().GetFileSpec().GetFilename()
					frame.path = _frame.GetLineEntry().GetFileSpec().GetDirectory()+"/"+_frame.GetLineEntry().GetFileSpec().GetFilename()
					frame.line = _frame.GetLineEntry().GetLine()
					if not frame.name: frame.name = "<null>"
					frame.disassembled = False
				else:
					# Function is undefined; Load module/assembly
					frame.name = _frame.GetSymbol().GetName()
					frame.path = _frame.GetLineEntry().GetFileSpec().GetFilename()
					#TODO: get address locations for disassembly
					frame.line = _frame.GetLineEntry().GetLine()
					if frame.default:
						frame.data = _frame.Disassemble()
					frame.disassembled = True
					if not frame.name: frame.name = "<null2>"

		# Cleanup disappeared threads from list
		for expanded in model_bt.Model.expanded:
			if expanded not in thread_ids:
				model_bt.Model.expanded.remove(expanded)

	def breakpoint(self, path, line):
		if not self.target:
			cerr("error creating breakpoint %s:%s; no target set."%(path,str(line)))
			return
		breakpoint = self.target.BreakpointCreateByLocation(path, line)
		if not breakpoint:
			cerr("error creating breakpoint %s:%s."%(path,str(line)))
			return
		if not breakpoint.IsValid():
			cerr("error creating breakpoint %s:%s; breakpoint not valid"%(path,str(line)))
			return
		bp = model_bp.Model.get(path, line)
		if not bp:
			cerr("error creating breakpoint %s:%s; breakpoint is null"%(path,str(line)))
			return
		bp.id = breakpoint.GetID()
		# location = breakpoint.GetLocationAtIndex(0)
		# if not location:
			# cerr("error finding breakpoint location.")
			# return
	
	def breakpoint_delete(self, path, line):
		if not self.target:
			cerr("error deleting breakpoint %s:%s; no target set."%(path,str(line)))
			return
		bp = model_bp.Model.get(path, line)
		if not bp:
			cerr("error deleting breakpoint %s:%s; breakpoint is null"%(path,str(line)))
			return
		self.target.BreakpointDelete(bp.id)
		

	def breakpoints_clear(self):
		if not self.target:
			cerr("error clearing breakpoints; no target set.")
			return
		self.target.DeleteAllBreakpoints()
	
	def select_frame(self, obj):
		if not self.process:
			cerr("error selecting frame; no running process.")
			return
		if isinstance(obj, model_bt.Thread):
			cerr("not a thread")
			return
		else:
			model_bt.Model.navigated = -1

		frame = obj
		if not frame or not frame.thread:
			cerr("error invalid frame.")
			return

		changed = False
		selected_thread = self.process.GetSelectedThread()
		if selected_thread.GetThreadID() != frame.thread.id:
			self.process.SetSelectedThreadByID(frame.thread.id)
			selected_thread = self.process.GetSelectedThread()
			changed = True
		selected_frame = selected_thread.GetSelectedFrame()
		if selected_frame.GetFrameID() != frame.number or changed:
			selected_thread.SetSelectedFrame(frame.number)
			selected_frame = selected_thread.GetSelectedFrame()
			changed = True

		if changed:
			self.backtrace()
		frame = model_bt.Model.selected.selected
		assert(frame.number == selected_frame.GetFrameID())
		assert(frame.thread.id == selected_thread.GetThreadID())

		model_src.Model.clear()
		if not frame.disassembled:
			model_src.Model.path = frame.path
			model_src.Model.line = frame.line
		else:
			model_src.Model.symbol = frame.name
			model_src.Model.data = frame.data
			model_src.Model.line = 1
		return changed

	def step_over(self):
		if not self.process:
			cerr("error stepping over; no running process.")
			return
		state = state_type_to_str(self.process.GetState())
		if state in ["stepping","stopped","crashed"]:
			self.process.GetSelectedThread().StepOver()
			self.operation = "stepping"

	def step_into(self):
		if not self.process:
			cerr("error stepping into; no running process.")
			return
		state = state_type_to_str(self.process.GetState())
		if state in ["stepping","stopped","crashed"]:
			self.process.GetSelectedThread().StepInto()
			self.operation = "stepping"

	def step_out(self):
		if not self.process:
			cerr("error stepping out; no running process.")
			return
		state = state_type_to_str(self.process.GetState())
		if state in ["stepping","stopped","crashed"]:
			self.process.GetSelectedThread().StepOut()
			self.operation = "stepping"

	def refresh(self, timeout=0, nesting=0):

		# The re-setting of the selected thread is absolutely neccessary
		# because lldb otherwise begins to misbehave when stepping outside
		# of the main thread
		tid = self.process.GetSelectedThread().GetThreadID()
		state = self.process_events(timeout)
		self.process.SetSelectedThreadByID(tid)

		# Ensure that we don't get stuck with infinite recursion
		if nesting > 1: pass

		if state == "invalid":
			if self.operation == "stepping":
				state = self.refresh(timeout, nesting+1)
		elif state == "unloaded":
			print("unloaded")
		elif state == "connected":
			print("connected")
		elif state == "attaching":
			print("attaching")
		elif state == "launching":
			print("launching")
		elif state == "stopped":
			self.operation = ""
			self.backtrace()
		elif state == "running":
			if self.operation == "stepping":
				state = self.refresh(timeout, nesting+1)
			else:
				print("running")
		elif state == "stepping":
			self.operation = ""
			self.backtrace()
		elif state == "crashed":
			self.operation = ""
			self.backtrace()
		elif state == "detached":
			print("detached")
		elif state == "exited":
			print("exited")
		elif state == "suspended":
			print("suspended")
		return state

	def process_events(self, timeout=0):
		if not self.process:
			return
		event = lldb.SBEvent()
		eventCount = 0
		state = self.process.GetState()
		state_new = self.process.GetState()
		done = False

		if state == lldb.eStateInvalid or state == lldb.eStateExited or not self.proc_listener:
		# if state == lldb.eStateExited or not self.proc_listener:
			pass

		import time;
		start = time.time()*1000.0
		while not done:
			elapsed = time.time()*1000.0
			if not self.proc_listener.PeekAtNextEvent(event):
				if elapsed - start < timeout:
					time.sleep(0.05)
				else:
					done = True
				# If no events in queue - wait X seconds for events
				# if timeout > 0:
					# self.proc_listener.WaitForEvent(timeout, event)
					# state_new = lldb.SBProcess.GetStateFromEvent(event)
					# eventCount = eventCount + 1
				# done = not self.proc_listener.PeekAtNextEvent(event)
			else:
				# If events are in queue - process them here
				self.proc_listener.GetNextEvent(event)
				state_new = lldb.SBProcess.GetStateFromEvent(event)
				eventCount = eventCount + 1
				if state_new == lldb.eStateInvalid:
					continue
				done = not self.proc_listener.PeekAtNextEvent(event)

		# View changes bubble up from here. First, they're handled on the controller
		# level in the refresh() function. Then, code bubbles up to plugin.py where
		# the state change is handled on the view level (MVC)
		return state_type_to_str(state_new)

