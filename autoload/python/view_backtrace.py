#!/usr/bin/env python
#
# view_backtrace.py 
# Copyright (c) 2017 owl
#

from model_backtrace import Model

class View:
	link = None

	def clear():
		if not link: return
		link.clear()

	def render():
		if not Model: return
		if not Model.threads: return

		link.clear()
		link.write("<Backtracke>")
		lineNum = 0
		for item in Model.threads:
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
					Model.sources[lineNum] = frame

	def info():
		cursor = link.window.get_cursor()
		frame = Model.sources(cursor[0])
		return frame

