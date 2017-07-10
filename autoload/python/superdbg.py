#!/usr/bin/env python

# Ability to load local scripts/modules
import os
import inspect
import sys
directory = os.path.dirname(inspect.getfile(inspect.currentframe()))
sys.path.append(directory)

import vim
import dbg

debugger = dbg.DebugController()
debugtab = None

# View represents a window within a tab
class View:
	# Create view from current vim perspective
	def __init__(self):
		self.tabpage = vim.current.tabpage
		self.window = vim.current.window
		self.buffer = vim.current.buffer

	def switch_to(self):
		vim.command(":tab "+str(self.tabpage.number))
		vim.command(":"+str(self.window.number)+' wincmd w')
		vim.command(":buffer "+str(self.buffer.number))
	
	def width(self):
		return int(vim.eval("winwidth('%')"))

	def height(self):
		return int(vim.eval("winheight('%')"))
		

class DebugTab:
	def __init__(self):
		self.original = View()
		
		# Open the debug tab
		vim.command(":tabnew")
		self.source = View()

		# Get view dimensions for proportional resizing
		winwidth = int(vim.eval("winwidth('%')"))
		winheight = int(vim.eval("winheight('%')"))

		# Split the backtrace window below the source one
		vim.command(":botright split [DEBUG BACKTRACE]")
		vim.command(":resize "+str(int(winheight/3)))
		vim.command(":enew")
		vim.current.buffer.name = "[DEBUG BACKTRACE]"
		self.backtrace = View()

		# Split the variables window to the right of the source/backtrace windows
		vim.command(":botright vsplit")
		vim.command(":vertical resize "+str(int(winwidth/3)))
		vim.command(":enew")
		vim.current.buffer.name = "[DEBUG VARIABLES]"
		self.variables = View()
	
		self.backtrace.switch_to()
		self.backtrace_index = {}

	def open_source(self, source, line):
		self.source.switch_to()
		vim.command(":e "+source)
		vim.command(":"+str(line))

	def dump_backtrace(self):
		callstack = debugger.callstack()
		if callstack is None or callstack.threads is None: return False

		self.backtrace_index = {}

		vim.current.buffer[0] = " Bactrace: "+"alpha"
		vim.current.buffer.append(70*"=")
		for t in callstack.threads:
			thread = callstack.threads[t]
			vim.current.buffer.append(("* "if thread.default else "  ")+"thread #"+str(t)+": "+thread.function)
			for f in thread.frames:
				frame = thread.frames[f]
				vim.current.buffer.append("|   "+("* "if frame.default else "- ")+"frame #"+str(f)+": "+frame.function)
				if(frame.has_source()):
					self.backtrace_index[len(vim.current.buffer)] = {'source':frame.source, 'line':frame.line}
					# vim.current.buffer.append("|    |  "+frame.source+"["+str(frame.line)+"]")
		return True



def Breakpoint(function=None, source=None, line=None):
	global debugger
	
	result = debugger.breakpoint(function, source, line)

def BacktraceGo():
	global debugtab
	# print("Writing from backtrace")
	# print(str(vim.current.line))

	line = vim.current.window.cursor[0]
	if line in debugtab.backtrace_index:
		index = debugtab.backtrace_index[line]
		debugtab.open_source(index['source'], index['line'])

	# debugtab.go_source(debugtab.backtrace_index

def Launch():
	global debugger
	global debugtab
	if(debugger):
		debugger.quit()
	debugger = dbg.DebugController()
	debugtab = DebugTab()

	# Shorter vim calls
	tabpage = vim.current.tabpage
	buffer = vim.current.buffer
	window = vim.current.window

	# Configure vim buffer options
	buffer.options['buflisted'] = False
	buffer.options['swapfile'] = False
	buffer.options['bufhidden'] = 'hide'
	buffer.options['buftype'] = 'nofile'
	buffer.options['modifiable'] = True

	# Configure vim window options
	window.options['number'] = False
	window.options['relativenumber'] = False

	if(debugger.initialize("~/Code/prototypes/alpha/bin/alpha")):
		pass
	else:
		return False

	if(debugger.breakpoint(function="main", source="main.cpp")):
		pass
	else:
		return False

	debugger.run()
	debugger.wait_for_break()


	debugtab.dump_backtrace()

	buffer.options['modifiable'] = False

	vim.command(":map <buffer> <Enter> : python3 BacktraceGo()<CR>")

	return debugger

def Quit():
	if(not debugger):
		return
	debugger.quit()




