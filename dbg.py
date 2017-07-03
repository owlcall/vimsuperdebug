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
# [x] Pause current program
# [x] Continue running program
# Quit debugging program
# [x] Step over function
# [x] Step into function
# [x] Step out of function

# Return local and global variables
# Re-assign local and global variables' values
# Watch variables (break if variable value changes)

# Query member variables for local objects
# Query member variables for global objects

# [x] Return call stack
# [x] Return list of threads
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

		# Format LLDB thread information output
		self.debug.write('''settings set thread-format "thread #${thread.index}: tid = ${thread.id%tid}{, ${frame.pc}}{ ${module.file.fullpath}{`${function.name-with-args}{${function.pc-offset}}}}{ at ${line.file.fullpath}:${line.number}}{, name = '${thread.name}'}{, queue = '${thread.queue}'}{, activity = '${thread.info.activity.name}'}{, ${thread.info.trace_messages} messages}{, stop reason = ${thread.stop-reason}}"''')

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
		print("Interrupting debugger to begin quitting process...")
		self.interrupt()
		self.debug.process.sendline("quit")
		i = self.debug.process.expect([".*?Do you really want to proceed", pexpect.EOF])
		if(i == 0):
			print("Quitting debugged applications")
			self.debug.write("Y")
			self.debug.process.expect(pexpect.EOF)
		
		print("Closing application")
		if(self.debug.process.isalive()):
			self.debug.close()
		

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

		self.debug.process.sendline('continue')
		self.debug.process.expect(".+?Process [0-9]* resuming")

		print("Continuing execution")
		return True

	# Step into call
	def step_into(self, count=1):
		# Ensure we're running first
		if(self.running is not True):
			return False

		self.debug.write("step")
		i = self.debug.process.expect(["error: (.*)\r\n", "(.+)\(lldb\) "])
		if(i == 0):
			print("Failed to step into the instruction.")
			return False
		elif(i == 1):
			print("Stepped into next frame")
		return True

	# Step over call
	def step_over(self, count=1):
		# Ensure we're running first
		if(self.running is not True):
			return False

		self.debug.write("next")
		i = self.debug.process.expect(["error: (.*)\r\n", "(.*)\(lldb\) "])
		if(i == 0):
			print("Failed to step over the instruction.")
			return False
		elif(i == 1):
			print("Stepped over the frame")
		return True

	# Step out of call
	def step_out(self, count=1):
		# Ensure we're running first
		if(self.running is not True):
			return False

		self.debug.write("finish")
		i = self.debug.process.expect(["error: (.*)\r\n", "(.*)\(lldb\) "])
		if(i == 0):
			print("Failed to step out of the instruction.")
			return False
		elif(i == 1):
			print("Stepped out of the frame")
		return True

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

		self.debug.process.expect("(.+)\r\n\(lldb\) ")
		print("BP RESUTS: "+self.debug.process.match.groups()[0])
		return True

	# Return the backtrace (call stack)
	def backtrace(self):
		if(self.initialized is False): return False
		
		self.debug.write("bt")
		self.debug.process.expect("\* thread.*?\r\n(.*)\(lldb\) ")

		return self.parse_frames(self.debug.process.match.groups()[0])

	# Return the thread list
	def threads(self):
		if(self.initialized is False): return False

		self.debug.write("thread list")
		self.debug.process.expect("Process\s\d*?\sstopped\r\n(.*)\(lldb\) ")

		return self.parse_threads(self.debug.process.match.groups()[0])



	def parse_frames(self, data):
		matches = re.findall(r"(\*?)?\s?frame\s#(\d*):\s([0-9a-fA-FxX]*)\s(.*?)`(.*?)\s\+\s(\d*)(?:\sat\s(\S*):(\d*))?", data, re.DOTALL)

		frames = []
		for match in matches:
			frames.append(Frame(*match))

		for frame in frames:
			frame.print()
		return frames

	def parse_threads(self, data):
		matches = re.findall(r"(\*?)?\s?thread\s#(\d*):\stid\s=\s([0-9a-fA-FxX]*),\s([0-9a-fA=FxX]*)\s(.*?)`(.*?)\s\+\s(\d*)(?:\sat\s(\S*):(\d*))?", data, re.DOTALL)

		threads = []
		for match in matches:
			threads.append(Thread(*match))

		for thread in threads:
			thread.print()
		return threads

	# At the time of running/continuing, we're often waiting on the debugger to stop at a breakpoint or after interruption, at this point we must be ready to intercept input and trigger results
	def wait_for_break(self):
		if(self.initialized is False or self.running is False): return False
		# self.debug.process.expect(".*?\*\sthread.*?\r\n(.*)")
		self.debug.process.expect("Process\s\d*?\sstopped\r\n(.*)")
		frames = self.parse_frames(self.debug.process.match.groups()[0])
		return frames

class Frame:
	# Initialize frame information from data
	def __init__(self, default, frame, memory, module_path, function, offset, source_path, source_line):
		self.default = True if(default == "*") else False
		self.frame = int(frame)
		self.memory = str(memory)
		self.module = str(module_path)
		self.function = str(function)
		self.offset = int(offset)
		self.source = str(source_path)
		self.line = int(source_line) if source_line is not '' else -1

	def print(self):
		print("------------------------------- FRAME")
		print(("*"if self.default else" ")+" f: "+str(self.frame)+" "+self.memory+" "+self.function)
		if(self.source):
			print("File: "+self.source+"["+str(self.line)+"]")
		else:
			print("File: unknown")

class Thread:
	# Initialize thread information from data
	def __init__(self, default, thread, tid, memory, module_path, function, offset, source_path, source_line):
		self.default = True if(default == "*") else False
		self.thread = int(thread)
		self.tid = str(tid)
		self.memory = str(memory)
		self.module = str(module_path)
		self.function = str(function)
		self.offset = int(offset)
		self.source = str(source_path)
		self.line = int(source_line) if source_line is not '' else -1

	def print(self):
		print("------------------------------- THREAD")
		print(("*"if self.default else" ")+" t: "+str(self.thread)+" "+self.memory+" "+self.function)
		if(self.source):
			print("File: "+self.source+"["+str(self.line)+"]")
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
dbg.threads()
assert(dbg.breakpoint(file="main.cpp", line=96))
dbg.resume()
dbg.wait_for_break()
dbg.threads()
dbg.backtrace()
# dbg.resume()
dbg.quit()

