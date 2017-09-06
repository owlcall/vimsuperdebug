#!/usr/bin/env python
#
# view_source.py 
# Copyright (c) 2017 owl
#

import vim
import vim_view
from model_source import Model

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
		if not c.link: return

		if Model.path:
			# Working with source file
			c.link.switch_to()
			vim.command(":nos e "+Model.path+"")
			vim.command(":"+str(Model.line))
		else:
			print("rendering assembly "+str(Model.symbol))
			c.link.switch_to()
			vim.command(":e [asm: "+str(Model.symbol)+"]")
			buf = vim_view.Buffer()
			buf.set_readonly(False)
			buf.set_nofile(True)
			buf.vim[:] = None
			for item in Model.data.split("\n"):
				buf.vim.append(item)
			vim.command(":"+str(Model.line))
			buf.set_readonly(True)


