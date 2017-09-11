#!/usr/bin/env python
#
# view_source.py 
# Copyright (c) 2017 owl
#

import vim
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

	# Render the source model
	@classmethod
	def render(c, model):
		if not c.link: return

		if model.path:
			# Working with source file
			c.link.switch_to()
			vim.command(":nos e "+model.path+"")
			vim.command(":"+str(model.line))
		else:
			c.link.switch_to()
			if not model.symbol:
				return
			vim.command(":e [asm: "+str(model.symbol)+"]")
			buf = view.Buffer()
			buf.set_readonly(False)
			buf.set_nofile(True)
			buf.vim[:] = None
			for item in model.data.split("\n"):
				buf.vim.append(item)
			buf.set_readonly(True)
			vim.command(":set syntax=asm")
			vim.command(":"+str(model.line))


