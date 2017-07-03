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
		# self.debug.write('settings set frame-format "frame #${frame.index}: ${frame.pc}{ ${module.file.fullpath}`${function.name-with-args}{${function.pc-offset}}}{ at ${line.file.fullpath}:${line.number}}"')
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
		
	# Return the backtrace (call stack)
	def backtrace(self):
		if(self.initialized is False): return False
		
		self.debug.write("bt")
		self.debug.process.expect("\* thread.*?\r\n(.*)")

		results = self.debug.process.match.groups()[0]
		matches = re.findall(r"(\*?)?\s?frame #(\d):\s([0-9a-fA-FxX]*)\s(.*?)`(.*?)\r\n", results, re.DOTALL)
		for match in matches:
			# Parse out the function string from possible options:
			#: main(arch=1, argv=0x000000abcdef) at main.cpp:51
			#: Greeter.hasMet(name="Anton", self=0x0000000101200190) -> Bool + 24 at Greeter.swift:5
			#: Greeter.greet(name="Anton", self=0x0000000101200190) -> () + 84 at Greeter.swift:9
			#: main + 155 at Greeter.swift:20
			#: start + 1

			# Extract the 5th capture group:
			data = match[4]
			expr = re.compile(r"(.*)?\s(?:\+\s(\d*)\sat\s(\S*):(\d*)|\+\s(\d*)|at\s(\S*):(\d*))")
			sigmatch = re.match(expr, data)
			datamatch = sigmatch
			if(datamatch is None):
				datamatch = ""
			else:
				datamatch = str(datamatch.groups())

			default = False
			if(match[0] == "*"): default = True
			frameID = match[1]
			memory = match[2]
			module = match[3]

			symbol = sigmatch[1]

			# First variable (+ offset at location:line)
			offset = 0 if sigmatch[2] is None else sigmatch[2]
			location = "" if sigmatch[3] is None else sigmatch[3]
			line = -1 if sigmatch[4] is None else sigmatch[4]

			# Second variation (+ offset)
			offset = offset if sigmatch[5] is None else sigmatch[5]

			# Third variation (at location:line)
			location = location if sigmatch[6] is None else sigmatch[6]
			line = line if sigmatch[7] is None else sigmatch[7]
			
			if(default): frameID = str(frameID)+"*"
			else: frameID = str(frameID)+" "
			output = "Fr: "+str(frameID)+" mem: "+str(memory)+" module: "+str(module)
			output = output + "\t"+str(symbol)
			if location:
				output = output+" "+str(location)+"["+str(line)+"]"

			print(output)



	# At the time of running/continuing, we're often waiting on the debugger to stop at a breakpoint or after interruption, at this point we must be ready to intercept input and trigger results
	def wait_for_break(self):
		if(self.initialized is False or self.running is False): return False

		self.debug.process.expect(".+Process (\d+) stopped.*\* thread #(\d+).*frame #(\d+): ([0-9a-fA-FxX]*) (\w*)`(.*) at ([0-9a-zA-Z]*?\.?[0-9a-zA-Z]*?):(\d*)")
		print("--------------- BREAK")

		frame = Frame(*self.debug.process.match.groups())
		frame.print()

class Frame:
	def __init__(self, procID, threadID, frameID, memoryLocation, binaryName, funcSignature, fileName, lineNumber):
		self.procID = procID
		self.threadID = threadID
		self.frameID = frameID
		self.memory = memoryLocation
		self.binary = binaryName
		self.function = funcSignature
		self.file = fileName
		self.line = lineNumber

	def print(self):
		print("------------------------------- FRAME")
		print("PID: "+str(self.procID)+", TID: "+str(self.threadID)+", FID: "+str(self.frameID))
		print("MID: "+str(self.memory)+": "+str(self.function)+" "+self.binary+"@"+str(self.file)+"["+str(self.line)+"]")



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

