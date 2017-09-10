#!/usr/bin/env python
#
# view_backtrace.py 
# Copyright (c) 2017 owl
#

import view

class View:
	link = None

	@classmethod
	def initialize(c):
		c.link = view.Link()

	@classmethod
	def valid(c):
		return c.link != None

	@classmethod
	def clear(c):
		if not c.link: return
		c.link.clear()

	@classmethod
	def render(c, model):
		if not model: return
		if not model.threads: return

		c.link.tab.window.buffer.set_readonly(False)
		c.link.clear()
		c.link.write("<Backtracke>")
		lineNum = 2
		lineNav = -1
		for item in model.threads:
			line = ""
			if item.default: line = line + "*"
			else: line = line + " "
			line = line + "Thread #"+str(item.number)
			lineNum = lineNum + 1
			c.link.write(line)
			model.sources[lineNum] = item

			if model.navigated == item.number:
				lineNav = lineNum

			if not item.default and item.id not in model.expanded:
				continue
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
					line = line + "("+frame.file+" "+pathLine+")"
				lineNum = lineNum + 1
				c.link.write(line)
				if frame.default:
					c.link.tab.window.set_cursor(lineNum,1)
				model.sources[lineNum] = frame

		if lineNav > 0:
			c.link.tab.window.set_cursor(lineNav, 1)

		c.link.tab.window.buffer.set_readonly(True)

	@classmethod
	def info(c, model):
		if not model.sources:
			print("source listing to navigate")
			return
		cursor = c.link.tab.window.get_cursor()
		if not cursor[0] in model.sources:
			return
		frame = model.sources[cursor[0]]
		return frame

