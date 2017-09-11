#!/usr/bin/env python
#
# view_source.py 
# Copyright (c) 2017 owl
#

import vim
import view

class View:
	link = None
	model = None

	@classmethod
	def initialize(c, model):
		vim.command(":silent enew")
		vim.command(":nmap <silent> <Leader>o : python StepOut()<CR>")
		vim.command(":nmap <silent> <Leader>i : python StepInto()<CR>")
		vim.command(":nmap <silent> <Leader>n : python StepOver()<CR>")
		c.link = view.Link()
		c.link.tab.window.buffer.set_nofile(True)
		c.model = model

	@classmethod
	def valid(c):
		return c.link != None

	@classmethod
	def clear(c):
		if not c.link: return
		c.link.clear()

	# Render the source model
	@classmethod
	def render(c):
		if not c.link: return
		if not c.model: return
		if not c.model.path and not c.model.data: return
		if not c.model.changed: return
		c.model.changed = False

		c.link.tab.switch()
		c.link.tab.window.switch()

		if c.model.path:
			# Working with source file
			c.link.switch_to()
			vim.command(":silent nos e "+c.model.path+"")
			c.link.tab.window.set_cursor(c.model.line, c.model.column)
		elif c.model.data:
			c.link.switch_to()
			if not c.model.symbol:
				return
			vim.command(":silent e ["+str(c.model.symbol)+"]")
			buf = view.Buffer()
			buf.set_readonly(False)
			buf.set_nofile(True)
			buf.vim[:] = None
			for item in c.model.data.split("\n"):
				if len(buf.vim) == 1 and not buf.vim[0]:
					buf.vim[len(buf.vim)-1] = item
				else:
					buf.vim.append(item)
			buf.set_readonly(True)
			vim.command(":set syntax=asm")
			# c.link.tab.window.set_cursor(c.model.line, c.model.column)
			vim.command(":"+str(len(buf.vim)-1))
		else:
			print("ERROR CAN'T FIND MODEL FOR SOURCE")
			


