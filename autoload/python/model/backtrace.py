#!/usr/bin/env python
#
# model_backtrace.py 
# Copyright (c) 2017 owl
#

class Frame:
	def __init__(self):
		self.default = False
		self.number = None
		self.thread = None
		self.disassembled = False

		# Module and function/symbol information
		self.module = ""
		self.name = ""

		# Source file information
		self.path = ""
		self.line = 0
		self.column = 0

		# Disassembly information
		self.data = ""		# used for assembly source (since no file exists)
		self.addressStart = ""
		self.addressEnd = ""
		self.addressCurrent = ""

class Thread:
	def __init__(self):
		self.frames = []
		self.frame_current = None
		self.default = False
		self.number = None
		self.id = 0

	def frame(self):
		frame = Frame()
		frame.thread = self
		self.frames.append(frame)
		Model.changed = True
		return frame

class Model:
	sources = {}	# indexed by line numbers, stores frame
	threads = []
	selected = None
	expanded = []
	navigated = -1
	changed = True

	@classmethod
	def fold(c, id):
		if id in c.expanded:
			c.expanded.remove(id)
		else:
			c.expanded.append(id)
		c.changed = True

	@classmethod
	def clear(c, total=False):
		c.sources = {}
		c.threads = []
		c.selected = None
		# If not total - then we maintain folds while navigating backtrace 
		# total is used when program exits and backtrace must be clear
		if total:
			c.expanded = []
			c.navigated = -1
		c.changed = True
	
	@classmethod
	def thread(c):
		thread = Thread()
		c.threads.append(thread)
		c.changed = True
		return thread

