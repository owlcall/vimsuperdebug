#!/usr/bin/env python

import subprocess
import pexpect

# Interface for interacting with the debugger in an intuitive manner


class Process:
	def __init__(self):
		self.process = None
		self.input = None
		self.output = None
		self.errors = None

	def is_open(self):
		if(self.process is not None):
			return True;
		return False

	def open(self, process):
		if(self.is_open()):
			print('Can\'t open process "'+process+'" because another process is already open.\nExisting process is "'+self.process+'"')
			return False
		self.process = pexpect.spawnu(process)
		self.process.expect(".+\(lldb\) ")
		return True

	def read(self):
		return self.readexp("(.+)\(lldb\) ")

	def readexp(self, expression):
		try:
			self.process.expect(expression)
		except:
			self.close()
			return ""
		return self.process.match.groups()[0]

	def expect(self, expression):
		return self.process.expect(expression)

	def write(self, data):
		self.process.sendline(data)
		self.process.expect('\r\n')		# Skip the line which was sent as input
		return True

	def close(self):
		result = self.process.terminate(force=True)
		self.process = None
		return result






# Set breakpoint line
# Set breakpoint function/method

# [x] Run given program
# Pause current program
# Continue running program
# Quit debugging program
# Step over function
# Step into function
# Step out of function

# Return local and global variables
# Re-assign local and global variables' values
# Watch variables (break if variable value changes)

# Query member variables for local objects
# Query member variables for global objects

# Return list of threads
# Return current thread ID
# Switch to another thread as context (globals shared, locals changed)

class DBG:
	def __init__(self):
		print("DBG class instantiated")
		self.program = None
		self.debug = Process()
		self.debug.open("lldb")

		self.initialized = False
		self.running = False

	# Set program which will be used for debugging
	def initialize(self, path):
		if(self.program is not None):
			return False
		self.program = path
		
		# Create target executable for LLDB, and ensure we were successful
		self.debug.write('target create "'+path+'"')
		i = self.debug.process.expect(["error: (.*)\r\n", "Current executable set to '(.*)'.*\((.*)\).\r\n"])
		if(i == 0):
			print("Failed to initialize executable for debugging.")
			print("Error: "+self.debug.process.match.groups()[0])
			self.initialized = False
		elif(i == 1):
			print("Successfully initalized executable for debugging.")
			print("Executable: "+self.debug.process.match.groups()[0])
			print("Architecture: "+self.debug.process.match.groups()[1])
			self.initialized = True
		return self.initialized

	# Run given program
	def run(self):
		if(self.initialized is False):
			return False
		self.debug.write('run')
		i = self.debug.process.expect(["error: (.*)\r\n", "Process (\d+) launched: '(.*)' \((.*)\)."])
		if(i == 0):
			print("Failed to launch debug program.")
			print("Error: "+self.debug.process.match.groups()[0])
			self.running = False
		elif(i == 1):
			print("Successfully launched debug program.")
			self.running = True
		else:
			print("UNKNOWN THINGS HAPPEND IN RUN")
		return self.running

	# Step into call
	def step_into(self, count=1):
		# Ensure we're running first
		if(self.running is not True):
			return False

		self.debug.write("step")
		i = self.debug.process.expect(["error: (.*)\r\n", "(.+)\(lldb\)"])
		if(i == 0):
			print("Failed to step into the instruction.")
			return False
		elif(i == 1):
			print("Stepped to next frame")

dbg = DBG()
dbg.initialize("~/Code/prototypes/alpha/bin/alpha")
dbg.run()
