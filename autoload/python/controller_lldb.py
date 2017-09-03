#!/usr/bin/env python
#
# controller_lldb.py 
# Copyright (c) 2017 owl
#

import sys
import lldb

# Import models which are changed by the controller
from model_backtrace import Model as Backtrace

def cerr(data):
	sys.stderr.write(data)

class Controller:
	def __init__(self):
		print("Setting up LLDB")
		self.dbg = lldb.SBDebugger.Create()
		self.commander = self.dbg.GetCommandInterpreter()
		self.target = None
		self.process = None

		self.pid = -1
		self.proc_listener = None
		self.timeoutEvents = 1		# Number of seconds we wait for events


	def run(self, program, args=[]):
		error = lldb.SBError()
		info = lldb.SBLaunchInfo(args.split(' '))

		# Create new target (args are supplied when launching)
		self.target = self.dbg.CreateTarget(path, None, None, True, error)
		if not error.Success():
			cerr("error creating target \"%s\". %s" %(program, str(error)))
			return

		# Launch target process
		self.process = self.target.Launch(info, error)
		if not error.Success():
			cerr("error launching process \"%s\". %s" %(program, str(error)))
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

	def pause(self, program):
		if not self.process:
			cerr("error pausing. No running process.")
			return
		self.process.Stop()
		self.process_events(self.timeoutEvents)

	def resume(self):
		if not self.process:
			cerr("error resuming. No running process.")
			return
		self.process.Continue()
		self.process_events(self.timeoutEvents)

	def backtrace(self):
		if not self.process:
			cerr("error getting backtrace. No running process.")
			return

		threadSelected = self.process.GetSelectedThread() 
		frameSelected = threadSelected.GetSelectedFrame()
		for _thread in self.process:
			thread = Thread()
			thread.default = True if threadSelected == _thread else False
			thread.number = _thread.GetThreadID()

			for _frame in thread:
				frame = Frame()
				frame.default = True if frameSelected == _frame else False
				frame.number = _frame.GetFrameID()
				frame.module = _frame.GetModule().GetFileSpec().GetFilename()

				function = _frame.GetDisplayFunctionName()
				if function:
					frame.name = _frame.GetFunctionName()
					frame.path = _frame.GetLineEntry().GetFileSpec().GetFilename()
					frame.line = _frame.GetLineEntry().GetLine()
					frame.column = _frame.GetLineEntry().GetColumn()
				else:
					# Function is undefined; Load module/assembly
					# frame.path = frame.module
					frame.name = _frame.GetSymbol().GetName()
					frame.path = _frame.GetLineEntry().GetFileSpec().GetFilename()
					#TODO: get address locations for disassembly
					frame.line = _frame.GetLineEntry().GetLine()
					frame.column = _frame.GetLineEntry().GetColumn()
					frame.data = _frame.Disassemble()

	def breakpoint(self, path, line):
		breakpoint = self.target.BreakpointCreateByLocation(path, line)
		if not breakpoint:
			cerr("error setting breakpoint.")
			return
		if not breakpoint.IsValid():
			cerr("error setting breakpoint - breakpoint not valid")
			return
		location = breakpoint.GetLocationAtIndex(0)
		if not location:
			cerr("error finding breakpoint location.")
			return

	def step_over(self):
		if not self.process:
			cerr("error stepping over. No running process.")
			return
		self.process.GetSelectedThread().StepOver()
		self.process_events(self.timeoutEvents)

	def step_into(self):
		if not self.process:
			cerr("error stepping into. No running process.")
			return
		self.process.GetSelectedThread().StepInto()
		self.process_events(self.timeoutEvents)

	def step_out(self):
		if not self.process:
			cerr("error stepping out. No running process.")
			return
		self.process.GetSelectedThread().StepOut()
		self.process_events(self.timeoutEvents)

	def refresh(self):
		process_events(self)

	def process_events(self, timeout=0):
		if not self.process:
			return
		event = lldb.SBEvent()
		eventCount = 0
		state = self.process.GetState()
		state_new = None
		done = False

		if state == lldb.eStateInvalid or state == lldb.eStateExited or not self.proc_listener:
			pass

		while not done:
			if not self.proc_listener.PeekAtNextEvent(event):
				# If no events in queue - wait X seconds for events
				if timeout > 0:
					self.proc_listener.WaitForEvent(timeout, event)
					state_new = lldb.SBProcess.GetStateFromEvent(event)
					eventCount = eventCount + 1
				done = not self.processListener.PeekAtNextEvent(event)
			else:
				# If events are in queue - process them here
				self.proc_listener.GetNextEvent(event)
				state_new = lldb.SBProcess.GetStateFromEvent(event)
				eventCount = eventCount + 1
				done = not self.processListener.PeekAtNextEvent(event)

		#TODO: interact with state_new to see how it compares to state
		#TODO: this is where the view change could be triggered!
		pass

global controller
controller = Controller()

