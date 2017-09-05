#!/usr/bin/env python
#
# model_backtrace.py 
# Copyright (c) 2017 owl
#

class Frame:
	def __init__(self):
		default = False
		number = None
		thread = None

		# Module and function/symbol information
		module = ""
		name = ""

		# Source file information
		path = ""
		line = 0
		column = 0

		# Disassembly information
		data = ""		# used for assembly source (since no file exists)
		addressStart = ""
		addressEnd = ""
		addressCurrent = ""

class Thread:
	def __init__(self):
		frames = []
		frame_current = None
		default = False
		number = None

class Model:
	sources = []	# indexed by line numbers, stores frame
	threads = []
	thread_current = None

	@classmethod
	def clear(c):
		c.sources = []
		c.threads = []
		c.thread_current = None

