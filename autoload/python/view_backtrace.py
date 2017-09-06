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

		c.link.tab.window.buffer.set_readonly(False)
		c.link.clear()
		c.link.write("<Backtracke>")
		lineNum = 2
		for item in Model.threads:
			line = ""
			if item.default: line = line + "*"
			else: line = line + " "
			line = line + "Thread #"+str(item.number)
			lineNum = lineNum + 1
			c.link.write(line)

			if not item.default:
				continue
			# if item.frames:
			for frame in item.frames:
				line = "\t"
				if frame.default:
					line = line + "*"
				else:
					line = line + " "
				line = line + "Frame #"+str(frame.number)+" "
				line = line + frame.name+" "
				if frame.path:
					pathLine = "["+str(frame.line)+"]" if frame.line else ""
					line = line + "("+frame.path+" "+pathLine+")"
				lineNum = lineNum + 1
				c.link.write(line)
				if frame.default:
					c.link.tab.window.set_cursor(lineNum,1)

				Model.sources[lineNum] = frame
				# print(lineNum, frame.path)
		c.link.tab.window.buffer.set_readonly(True)

	@classmethod
	def info(c):
		if not Model.sources:
			print("source listing to navigate")
			return
		cursor = c.link.tab.window.get_cursor()
		if not cursor[0] in Model.sources:
			return
		frame = Model.sources[cursor[0]]
		return frame

