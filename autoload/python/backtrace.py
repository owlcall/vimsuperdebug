#!/usr/bin/env python
#
# view_backtrace.py 
# Copyright (c) 2017 owl
#

class Frame:
	path = ""
	data = ""		# used for assembly source (since no file exists)
	line = 0
	function = ""
	default = False
	number = None

class Thread:
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

class View:
	link = None
	model = None

	def clear():
		if not link: return
		link.clear()

	def render():
		if not model: return
		if not model.threads: return

		link.clear()
		link.write("<Backtracke>")
		lineNum = 0
		for item in model.threads:
			line = ""
			if item.default:
				line = line + "* "
			line = line + "Thread #"+str(item.number))
			lineNum = lineNum + 1
			link.write(line)

			if item.frames:
				for frame in item.frames:
					line = ""
					if frame.default:
						line = "* "
					line = line + "Frame #"+str(frame.number)+" "
					line = line + frame.function+" "
					line = line + "("+frame.path+"["+frame.line+"])"
					model.sources[lineNum] = frame

	def info():
		cursor = link.window.get_cursor()
		frame = model.sources(cursor[0])
		return frame

