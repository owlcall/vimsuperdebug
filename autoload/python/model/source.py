#!/usr/bin/env python
#
# model_backtrace.py 
# Copyright (c) 2017 owl
#

class Model:
	changed = False
	path = ""	# Used for source files
	data = ""	# Used for disassembly
	line = 0
	column = 0
	symbol = ""

	@classmethod
	def clear(c):
		c.changed = True
		c.path = ""
		c.data = ""
		c.line = 0
		c.column = 0
		c.symbol = ""

	@classmethod
	def set_source(c, path, line, column):
		c.path = path
		c.line = line
		c.column = column
		c.changed = True

	@classmethod
	def set_disasm(c, symbol, data, line):
		c.symbol = symbol
		c.data = data
		c.line = line
		c.changed = True
