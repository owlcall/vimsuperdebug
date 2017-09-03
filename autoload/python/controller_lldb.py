#!/usr/bin/env python
#
# controller_lldb.py 
# Copyright (c) 2017 owl
#

import sys
import lldb

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

	def attach(self, pid=-1, pname="", host=""):
		if not pid and not pname:
			cerr("error attaching; nothing to attach to.")
			return
		if self.process:
			#TODO: enhance error message
			cerr("error attaching to process; already attached")
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

	def resume(self):
		if not self.process:
			cerr("error resuming. No running process.")
			return
		self.process.Continue()


	def step_over(self):
		if not self.process:
			cerr("error stepping over. No running process.")
			return
		self.process.GetSelectedThread().StepOver()

	def step_into(self):
		if not self.process:
			cerr("error stepping into. No running process.")
			return
		self.process.GetSelectedThread().StepInto()

	def step_out(self):
		if not self.process:
			cerr("error stepping out. No running process.")
			return
		self.process.GetSelectedThread().StepOut()

	def process_events(self):
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
				if self.timeoutEvents > 0:
					self.proc_listener.WaitForEvent(self.timeoutEvents, event)
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

