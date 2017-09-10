#!/usr/bin/env python
#
# model_backtrace.py 
# Copyright (c) 2017 owl
#

class Model:
	path = ""	# Used for source files
	data = ""	# Used for disassembly
	line = 0
	symbol = ""

	@classmethod
	def clear(c):
		c.path = ""
		c.data = ""
		c.line = 0
		c.symbol = ""

