#!/usr/bin/env python

import pexpect
import re

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
		self.process = pexpect.spawnu(process, timeout=None)
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
# [x] Quit debugging program
# [x] Step over function
# [x] Step into function
# [x] Step out of function

# Return locals, args, and global variables
# Re-assign local, args, and global variables' values
# Watch variables (break if variable value changes)

# [x] Return call stack
# [x] Return list of threads
# [x] Thread navigation
# [x] Frame navigation
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
		# self.debug.process.expect(".*")
		self.debug.process.expect([".+Process [0-9]* stopped\r\n", ".*"])

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
		# TODO: document created breakpoint
		print("BP RESUTS: "+self.debug.process.match.groups()[0])
		return True

	# Select next frame for interaction
	def frame_next(self):
		result = Thread.default.defaultFrame
		grabNext = False
		for frameId, frame in Thread.default.frames.items():
			if(grabNext):
				result = frame
				break
			if(frame.default): grabNext = True

		if(result.default):
			return False
		return self.frame_select(result.id)

	# Select next frame for interaction
	def frame_previous(self):
		result = Thread.default.defaultFrame
		grabLast = False
		for frameId, frame in Thread.default.frames.items():
			if(grabLast): break
			if(frame.default): grabLast = True
			else: result = frame

		if(result.default):
			return False
		return self.frame_select(result.id)
	
	# Select specific frame for interaction
	def frame_select(self, index):
		if(self.initialized is False): return False

		if(index not in Thread.default.frames):
			return False
		self.debug.write("frame select "+str(index))
		self.callstack()

	# Select next thread for interaction
	def thread_next(self):
		result = Thread.default
		grabNext = False
		for threadId, thread in Thread.map.items():
			if(grabNext):
				result = thread
				break
			if(thread.default): grabNext = True

		if(result.default):
			return False
		return self.thread_select(result.id)

	# Select next thread for interaction
	def thread_previous(self):
		result = Thread.default
		grabLast = False
		for threadId, thread in Thread.map.items():
			if(grabLast): break
			if(thread.default): grabLast = True
			else: result = thread

		if(result.default):
			return False
		return self.thread_select(result.id)
	
	# Select specific thread for interaction
	def thread_select(self, index):
		if(self.initialized is False): return False

		if(index not in Thread.map):
			return False
		self.debug.write("thread select "+str(index))
		self.callstack()
		return True

	# Update current call stack (thread and current thread frame)
	def callstack(self):
		if(self.initialized is False): return False
		
		Thread.clear()
			
		# Update the thread stack
		self.debug.write("thread list")
		self.debug.process.expect("Process\s\d*?\sstopped\r\n(.*)\(lldb\) ")
		matches = re.findall(r"(?:(\*)\sthread|\sthread)\s#(\d*):\stid\s=\s([0-9a-fA-FxX]*),\s([0-9a-fA=FxX]*)\s(.*?)`(.*?)(?:(?=\*\sthread)|(?=\sthread)|\s\+\s(\d*)(?:\sat\s(\S*):(\d*))?|$)", self.debug.process.match.groups()[0], re.DOTALL)
		for match in matches:
			Thread(*match)

		# Update the frame (call) stack
		self.debug.write("bt")
		self.debug.process.expect("\* thread.*?\r\n(.*)\(lldb\) ")
		matches = re.findall(r"(?:(\*)\sframe|\sframe)\s#(\d*):\s([0-9a-fA-FxX]*)\s(.*?)`(.*?)(?:(?=\*\sframe)|(?=\sframe)|\s\+\s(\d*)(?:\sat\s(\S*):(\d*))?|$)", self.debug.process.match.groups()[0], re.DOTALL)
		if(len(matches) == 0):
			print(self.debug.process.match.groups()[0])
		for match in matches:
			Frame(Thread.default, *match)

		Thread.print()

	# Return the global variables
	def globals(self):
		pass

	# Return the local variables
	def locals(self):
		if(self.initialized is False or self.running is False): return False
		self.debug.write("frame variable")
		self.debug.process.expect("(.*?)\(lldb\) ")
		# print(self.debug.process.match.groups()[0])

		matches = re.findall(r"(?:(?:\((.*?)\)\s([a-zA-Z0-9_]*)\s=.*?)|.*?)\r\n", self.debug.process.match.groups()[0], re.DOTALL)
		for match in matches:
			if(match[0] == ''): continue
			print("|"+match[0]+"|"+match[1])
		pass

	# Return the function arguments
	def arguments(self):
		pass

	# At the time of running/continuing, we're often waiting on the debugger to stop at a breakpoint or after interruption, at this point we must be ready to intercept input and trigger results
	def wait_for_break(self):
		if(self.initialized is False or self.running is False): return False
		self.debug.process.expect("Process\s\d*?\sstopped\r\n(.*)")
		self.callstack()

class Variable:
	globals = {}
	locals = {}
	arguments = {}

	# Initialize variable
	def __init__(self, category, type, name, value):
		self.category = category
		self.type = type
		self.name = name
		self.value = value

class Thread:
	map = {}
	default = None

	# Initialize thread information from data
	def __init__(self, default, thread, tid, memory, module_path, function, offset, source_path, source_line):
		self.default = True if(default == "*") else False
		self.id = int(thread)
		self.tid = str(tid)
		self.memory = str(memory)
		self.module = str(module_path)
		self.function = str(function)
		self.offset = int(offset) if offset is not '' else -1
		self.source = str(source_path)
		self.line = int(source_line) if source_line is not '' else -1
		Thread.map[self.id] = self
		if(self.default):Thread.default = self
		
		self.frames = {}
		self.defaultFrame = None

	def hasOffset():
		if(offset != -1):
			return True
		return False

	def hasSource():
		if(self.source and self.line != -1):
			return True
		return False

	def clear():
		Thread.map = {}
		Thread.default = None

	def print():
		print("================= Callstack ================")
		for threadId,thread in Thread.map.items():
			print((">>"if thread.default else"  ")+" T: "+str(threadId)+" | "+thread.function)
			for frameId,frame in thread.frames.items():
				print("\t"+(">>"if frame.default else"  ")+" F: "+str(frameId)+" | "+frame.function)
		print("============================================")

class Frame:
	# Initialize frame information from data
	def __init__(self, thread, default, frame, memory, module_path, function, offset, source_path, source_line):
		self.default = True if(default == "*") else False
		self.id = int(frame)
		self.memory = str(memory)
		self.module = str(module_path)
		self.function = str(function)
		self.offset = int(offset) if offset is not '' else -1
		self.source = str(source_path)
		self.line = int(source_line) if source_line is not '' else -1

		thread.frames[self.id] = self
		if(self.default):thread.defaultFrame = self

	def hasSource():
		if(self.source and self.line != -1):
			return True
		return False


dbg = DBG()
dbg.initialize("~/Code/prototypes/alpha/bin/alpha")
assert(dbg.breakpoint(function="main", file="main.cpp"))
dbg.run()
dbg.wait_for_break()
# dbg.interrupt()
dbg.callstack()
assert(dbg.breakpoint(file="main.cpp", line=96))
dbg.resume()
dbg.wait_for_break()
dbg.callstack()
dbg.frame_next()
dbg.callstack()
# print("Looking at next thread")
# for i in range(0,15):
	# dbg.thread_next()
	# for j in range(0,10):
		# dbg.frame_next()
	# for j in range(0,10):
		# dbg.frame_previous()

# for i in range(0,15):
	# dbg.thread_previous()
	# for j in range(0,10):
		# dbg.frame_next()
	# for j in range(0,10):
		# dbg.frame_previous()
dbg.frame_previous()
dbg.locals()

dbg.resume()
dbg.interrupt()
# dbg.resume()

dbg.quit()

