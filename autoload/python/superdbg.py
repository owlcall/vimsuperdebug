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
		if(vim.current.tabpage.number != self.tabpage.number):
			vim.command(":tab "+str(self.tabpage.number))
		if(vim.current.window.number != self.window.number):
			vim.command(":"+str(self.window.number)+' wincmd w')
		if(vim.current.buffer.number != self.buffer.number):
			vim.command(":buffer "+str(self.buffer.number))
	
	def width(self):
		return int(vim.eval("winwidth('%')"))

	def height(self):
		return int(vim.eval("winheight('%')"))
		




class DebugTab:
	def __init__(self):
		self.original = View()
		
		# Open the debug tab, save the source view
		vim.command(":tabnew")
		self.source = View()

		vim.command(":enew")
		# TODO Configure buffer to be hidden/etc
		vim.current.buffer.name = "[DISASSEMBLY]"
		self.disasm = View()
	
		# Get view dimensions for proportional resizing
		winwidth = int(vim.eval("winwidth('%')"))
		winheight = int(vim.eval("winheight('%')"))

		# Split the backtrace window below the source one
		vim.command(":botright split [DEBUG BACKTRACE]")
		vim.command(":resize "+str(int(winheight/3)))
		vim.command(":enew")
		vim.command(":map <silent> <buffer> <Enter> : python3 BacktraceGo()<CR>")
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
		vim.command(":redraw")		# Fix cursor bug (cursor can be on line number ruler)
	
	def open_assembly(self, source, line):
		self.disasm.switch_to()
		self.disasm.buffer[:] = None	# Clear assembly buffer
		self.disasm.buffer.append(source)
		vim.command(":"+str(line))
		vim.command(":redraw")

	def dump_backtrace(self):
		callstack = debugger.callstack()
		if callstack is None or callstack.threads is None: return False

		self.backtrace_index = {}

		frameLine = 1
		vim.command(":%d _")	# Clear the buffer
		vim.current.buffer[0] = " Bactrace: "+"alpha"
		vim.current.buffer.append(self.backtrace.width()*"=")
		for t in callstack.threads:
			thread = callstack.threads[t]
			vim.current.buffer.append(("* "if thread.default else "  ")+"thread #"+str(t)+": "+thread.function)
			for f in thread.frames:
				frame = thread.frames[f]
				vim.current.buffer.append("|   "+("* "if frame.default else "- ")+"frame #"+str(f)+": "+frame.function)
				if(frame.default):
					frameLine = len(vim.current.buffer)
				if(frame.has_source()):
					self.backtrace_index[len(vim.current.buffer)] = {'source':frame.source, 'line':frame.line, 'assembly':False}
				else:
					self.backtrace_index[len(vim.current.buffer)] = {'assembly':True}
					# vim.current.buffer.append("|    |  "+frame.source+"["+str(frame.line)+"]")

		# Navigate to current backtrace line, and open the source
		vim.current.window.cursor = (frameLine, 1)
		curframe = callstack.selection.selection
		if(curframe.has_source()):
			self.open_source(curframe.source, curframe.line)
		return True




def Breakpoint(function=None, source=None, line=None):
	global debugger
	
	result = debugger.breakpoint(function, source, line)

def BacktraceGo():
	global debugger
	global debugtab
	# print("Writing from backtrace")
	# print(str(vim.current.line))

	line = vim.current.window.cursor[0]
	if line in debugtab.backtrace_index:
		index = debugtab.backtrace_index[line]
		if index['assembly'] is False:
			debugtab.open_source(index['source'], index['line'])
		else:
			assembly = debugger.disassembly()
			if assembly is False:
				print("Failed to get assembly information")
			else:
				print("Writing to buffer")
				debugtab.open_assembly(assembly[0], assembly[1])

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

	vim.command(":redraw")
	if(debugger.initialize("~/Documents/Code/prototypes/alpha/bin/alpha")):
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

	return debugger

def Quit():
	if(not debugger):
		return
	debugger.quit()




