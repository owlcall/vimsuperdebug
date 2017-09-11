#!/usr/bin/env python
#
# view_backtrace.py 
# Copyright (c) 2017 owl
#

import vim
import view

class View:
	link = None
	model = None
	line_frame = 1
	line_thread = 1
	line_current = 1

	@classmethod
	def initialize(c, model):
		vim.command(":silent e [BACKTRACE]")
		vim.command(":nmap <silent> <buffer> <Enter> : python BacktraceNavigate()<CR>")
		c.link = view.Link()
		c.model = model
		c.link.tab.window.buffer.set_readonly(True)
		c.link.tab.window.buffer.set_nofile(True)

	@classmethod
	def valid(c):
		return c.link != None

	@classmethod
	def clear(c):
		if not c.link: return
		c.link.clear()
		c.line_frame = 1
		c.line_thread = 1
		c.line_current = 1
	
	@classmethod
	def reset_cursor(c):
		if not c.link: return
		c.link.tab.window.set_cursor(c.line_frame, 1)

	@classmethod
	def render(c):
		if not c.link: return
		if not c.model: return
		if not c.model.threads: return
		if not c.model.changed:
			return
		c.model.changed = False

		c.link.switch_to()
		c.link.tab.window.buffer.set_readonly(False)
		c.link.clear()
		c.link.write("<Backtracke>")
		lineNum = 2
		lineNav = -1
		# Render every thread, and selected/unfolded threads' frames
		for item in c.model.threads:
			line = ""
			if item.default:
				line = line + "*"
				c.line_thread = lineNum+1
			else: line = line + " "
			line = line + "Thread #"+str(item.number)
			line = line + " id="+str(item.id)
			lineNum = lineNum + 1
			c.link.write(line)

			# Update model source index for thread folding
			c.model.sources[lineNum] = item

			if c.model.navigated == item.number:
				lineNav = lineNum

			# If thread not selected, and not expanded - don't render frames
			if not item.default and item.id not in c.model.expanded:
				continue
			# Render every frame in thread item
			for frame in item.frames:
				line = "\t"
				if frame.default:
					line = line + "*"
					c.line_frame = lineNum+1
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

				# Update model source index for backtrace navigation
				c.model.sources[lineNum] = frame

		# Select current backtrace line, and mark it readonly
		if lineNav >= 0:
			c.link.tab.window.set_cursor(lineNav, 1)
			c.line_current = lineNav
		c.link.tab.window.buffer.set_readonly(True)

	# Return thread/frame object from the source index
	# TODO: move this into model, indexed by line cursor
	@classmethod
	def info(c):
		if not c.link: return
		if not c.model: return
		if not c.model.sources: return
		cursor = c.link.tab.window.get_cursor()
		if not cursor[0] in c.model.sources:
			return
		frame = c.model.sources[cursor[0]]
		return frame

