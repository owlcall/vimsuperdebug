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
		elif Model.data:
			c.link.switch_to()
			vim.command(":enew")
			vim.command(":"+str(Model.line))
			vim.command(":file "+str(Model.symbol))
			c.link.write(Model.data)
			c.link.tab.window.buffer.set_readonly(True)
			c.link.tab.window.buffer.set_nofile(True)


