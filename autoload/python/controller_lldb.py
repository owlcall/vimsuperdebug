#!/usr/bin/env python
#
# controller_lldb.py 
# Copyright (c) 2017 owl
#

import sys
import import_lldb
import lldb

# Import models which are changed by the controller
from model_backtrace import Model as Backtrace
from model_breakpoints import Breakpoint as Breakpoints
from model_source import Model as Sources

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
			cerr("error creating target \"%s\". Not initialized."%(program))
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
		for _, group in Breakpoints.container.iteritems():
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
			#TODO: enhance error message
			cerr("error attaching to process; already attached")
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
		Breakpoints.unset_all()

	def pause(self, program):
		if not self.process:
			cerr("error pausing. No running process.")
			return
		self.process.Stop()

	def resume(self):
		if not self.process:
			cerr("error resuming. No running process.")
			return
		self.process.Continue()

	def backtrace(self):
		if not self.process:
			cerr("error getting backtrace. No running process.")
			return

		Backtrace.clear()
		threadSelected = self.process.GetSelectedThread() 
		frameSelected = threadSelected.GetSelectedFrame()
		for _thread in self.process:
			thread = Backtrace.thread()
			thread.default = True if threadSelected == _thread else False
			thread.number = _thread.GetIndexID()
			if thread.default:
				Backtrace.selected = thread

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

	def breakpoint(self, path, line):
		if not self.target:
			cerr("error creating breakpoint %s:%s. No target set."%(path,str(line)))
			return
		breakpoint = self.target.BreakpointCreateByLocation(path, line)
		if not breakpoint:
			cerr("error creating breakpoint %s:%s."%(path,str(line)))
			return
		if not breakpoint.IsValid():
			cerr("error creating breakpoint - %s:%s breakpoint not valid"%(path,str(line)))
			return
		location = breakpoint.GetLocationAtIndex(0)
		if not location:
			cerr("error finding breakpoint location.")
			return

	def breakpoints_clear(self):
		if not self.target:
			cerr("error clearing breakpoints. No target set.")
			return
		self.target.DeleteAllBreakpoints()
	
	def select_frame(self, frame):
		if not self.process:
			cerr("error selecting frame. No running process.")
			return
		if not frame or not frame.thread:
			cerr("error invalid frame.")
			return
		changed = False
		selected_thread = self.process.GetSelectedThread()
		if selected_thread.GetIndexID() != frame.thread.number:
			self.process.SetSelectedThreadByIndexID(frame.thread.number)
			selected_thread = self.process.GetSelectedThread()
			changed = True

		selected_frame = selected_thread.GetSelectedFrame()
		if selected_frame.GetFrameID() != frame.number or changed:
			selected_thread.SetSelectedFrame(frame.number)
			changed = True

		frame = Backtrace.selected.selected

		if changed:
			self.backtrace()
		Sources.clear()
		if not frame.disassembled:
			Sources.path = frame.path
			Sources.line = frame.line
		else:
			Sources.symbol = frame.name
			Sources.data = frame.data
			Sources.line = 1
		return changed

	def step_over(self):
		if not self.process:
			cerr("error stepping over. No running process.")
			return
		self.process.GetSelectedThread().StepOver()
		state = state_type_to_str(self.process.GetState())
		if state in ["stepping","stopped","crashed"]:
			print("initiating stepping...")
			self.operation = "stepping"

	def step_into(self):
		if not self.process:
			cerr("error stepping into. No running process.")
			return
		self.process.GetSelectedThread().StepInto()
		state = state_type_to_str(self.process.GetState())
		if state in ["stepping","stopped","crashed"]:
			print("initiating stepping...")
			self.operation = "stepping"

	def step_out(self):
		if not self.process:
			cerr("error stepping out. No running process.")
			return
		self.process.GetSelectedThread().StepOut()
		state = state_type_to_str(self.process.GetState())
		if state in ["stepping","stopped","crashed"]:
			print("initiating stepping...")
			self.operation = "stepping"

	def refresh(self, timeout=0):
		state = self.process_events(timeout)
		if state == "invalid":
			if self.operation == "stepping":
				state = self.refresh(timeout)
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
			self.operation = ""
			self.backtrace()
		elif state == "running":
			if self.operation == "stepping":
				state = self.refresh(timeout)
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
		state_new = lldb.eStateInvalid
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

		# print("state changed from %s to %s"%(state_type_to_str(state), state_type_to_str(state_new)))
		# View changes bubble up from here. First, they're handled on the controller scale in the refresh() function. Then, code bubbles up to plugin.py where the state change is handled on the view's level
		return state_type_to_str(state_new)

