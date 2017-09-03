#!/usr/bin/env python
#
# model_backtrace.py 
# Copyright (c) 2017 owl
#

class Frame:
	def __init__(self):
		path = ""
		data = ""		# used for assembly source (since no file exists)
		line = 0
		module = ""
		name = ""		# can be function name or symbol
		default = False
		number = None

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

	def clear():
		sources = []
		threads = []
		thread_current = None

