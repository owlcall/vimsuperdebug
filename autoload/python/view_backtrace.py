#!/usr/bin/env python
#
# view_backtrace.py 
# Copyright (c) 2017 owl
#

import vim_view
from model_backtrace import Model

class View:
	link = None

	@classmethod
	def initialize(c):
		c.link = vim_view.Link()

	@classmethod
	def valid(c):
		return c.link != None

	@classmethod
	def clear(c):
		if not c.link: return
		c.link.clear()

	@classmethod
	def render(c):
		if not Model: return
		if not Model.threads: return

		c.link.clear()
		c.link.write("<Backtracke>")
		lineNum = 0
		for item in Model.threads:
			line = ""
			if item.default:
				line = line + "* "
			line = line + "Thread #"+str(item.number)
			lineNum = lineNum + 1
			c.link.write(line)

			if item.frames:
				for frame in item.frames:
					line = ""
					if frame.default:
						line = "* "
					line = line + "Frame #"+str(frame.number)+" "
					line = line + frame.function+" "
					line = line + "("+frame.path+"["+frame.line+"])"
					Model.sources[lineNum] = frame

	@classmethod
	def info(c):
		if not Model.sources:
			print("source listing to navigate")
			return
		cursor = c.link.tab.window.get_cursor()
		frame = Model.sources[cursor[0]]
		return frame

