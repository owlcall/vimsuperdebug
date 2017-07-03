#!/usr/bin/env python

import subprocess
import pexpect
import re

# Interface for interacting with the debugger in an intuitive manner

# TODO: disable timeout on the debug process executables (since debugging lasts indefinitely)

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






# [x] Set breakpoint line
# [x] Set breakpoint function/method

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
		self.paused = False

	# Set program which will be used for debugging
	def initialize(self, path):
		if(self.program is not None):
			return False
		self.program = path
		
		# Format LLDB frame information output
		self.debug.write('settings set frame-format "frame #${frame.index}: ${frame.pc}{ ${module.file.fullpath}`${function.name-with-args}{${function.pc-offset}}}{ at ${line.file.fullpath}:${line.number}}"')
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

	# Quit the program
	def quit(self):
		print("quit interrupting...")
		self.interrupt()
		print("writing quit to lldb...")
		self.debug.write("quit")
		print("closing lldb process...")
		self.debug.close()
		print("finished quit method")

	# Run given program
	def run(self):
		if(self.initialized is False): return False
		if(self.running is True): return False
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

	# Interrupt given program
	def interrupt(self):
		if(self.initialized is False): return False
		if(self.running is False): return False

		self.debug.process.sendcontrol('c')
		self.debug.process.expect(".*")
		# self.debug.process.expect(".+Process [0-9]* stopped\r\n")

		print("Interrupted execution")
		return True

	# Resume interrupted program
	def resume(self):
		if(self.initialized is False): return False
		if(self.running is False): return False

		self.debug.write('continue')
		self.debug.process.expect(".+?Process [0-9]* resuming\r\n")

		print("Continuing execution")
		return True

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

	# Set breakpoint by function name (and optionally file)
	# Set breakpoint by file name and line number
	def breakpoint(self, function=None, file=None, line=-1):
		if(self.initialized is False): return False

		argFile = ""
		if(file is not None and len(file) > 0): argFile = "-f "+file
		if(function is not None):
			self.debug.write("br s -n "+function+" "+argFile)
		elif(file is not None and line is not -1):
			self.debug.write("br s "+argFile+" -l "+str(line))
		else:
			assert(false)

		self.debug.process.expect("(.+)\r\n")
		print("BP RESUTS: "+self.debug.process.match.groups()[0])
		return True
	

	def parse_frames(self, data):
		# Parse out frame information
		# Format:
		# * frame #0: 0x0000abcd /path/to/module`symbol + offset at /path/to/file:line
		matches = re.findall(r"(\*?)?\s?frame\s#(\d):\s([0-9a-fA-FxX]*)\s(.*?)`(.*?)\s\+\s(\d*)(?:\sat\s(\S*):(\d*))?", data, re.DOTALL)

		frames = []
		for match in matches:
			frames.append(Frame(*match))

		for frame in frames:
			frame.print()
		return frames


	# Return the backtrace (call stack)
	def backtrace(self):
		if(self.initialized is False): return False
		
		self.debug.write("bt")
		self.debug.process.expect("\* thread.*?\r\n(.*)")

		results = self.debug.process.match.groups()[0]
		self.parse_frames(results)



	# At the time of running/continuing, we're often waiting on the debugger to stop at a breakpoint or after interruption, at this point we must be ready to intercept input and trigger results
	def wait_for_break(self):
		if(self.initialized is False or self.running is False): return False
		self.debug.process.expect(".*?\*\sthread.*?\r\n(.*)")
		frames = self.parse_frames(self.debug.process.match.groups()[0])
		return frames

class Frame:
	# def __init__(self, procID, threadID, frameID, memoryLocation, binaryName, funcSignature, fileName, lineNumber):
	def __init__(self, default, frame, memory, module_path, function, offset, source_path, source_line):
		self.default = default
		self.frame = frame
		self.memory = memory
		self.module = module_path
		self.function = function
		self.offset = offset
		self.source = source_path
		self.line = source_line

	def print(self):
		print("------------------------------- FRAME")
		print(("*"if self.default else" ")+" f: "+self.frame+" "+self.memory+" "+self.function)
		if(self.source):
			print("File: "+self.source+"["+self.line+"]")
		else:
			print("File: unknown")


import time

dbg = DBG()
dbg.initialize("~/Code/prototypes/alpha/bin/alpha")
assert(dbg.breakpoint(function="main", file="main.cpp"))
dbg.run()
dbg.wait_for_break()
# time.sleep(10)
# dbg.interrupt()
dbg.backtrace()
# dbg.resume()
dbg.quit()

