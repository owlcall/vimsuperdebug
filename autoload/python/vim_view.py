#!/usr/bin/env python
#
# vim_view.py 
# Copyright (c) 2017 owl
#

import vim

class Buffer:
	def __init__(self):
		self.vim = vim.current.buffer
	
	def switch_to(self):
		if(vim.current.buffer.number != self.buffer.number):
			vim.command(":buffer "+str(self.buffer.number))

	def set_hidden(self, value):
		self.vim.options['buflisted'] = value
		self.vim.options['bufhidden'] = 'hide' if value else 'show'
	
	def set_readonly(self, value):
		self.vim.options['modifiable'] = not value

	def set_swap(self, value):
		self.vim.options['swapfile'] = value

	def set_nofile(self, value):
		self.vim.options['buftype'] = 'nofile' if value else 'file'
		self.vim.options['swapfile'] = not value

	def clear(self, line=-1):
		if line == -1: self.vim[:] = None
		else: self.vim[line] = ""
	
	def write(self, data, line=-1):
		if line == -1: self.vim.append(data)
		else: self.vim[line] = data

class Window:
	def __init__(self):
		self.vim = vim.current.window
		self.buffer = Buffer()

	def switch(self):
		if(vim.current.window.number != self.vim.number):
			vim.command(":"+str(self.vim.number)+' wincmd w')

	def switch_to(self):
		self.switch()
		self.buffer.switch_to()
	
	def show_numbers(self, value):
		self.vim.options['number'] = value
		self.vim.options['relativenumber'] = value
	
	def set_cursor(self, line, column):
		self.vim.cursor = (line, column)

	def get_cursor(self):
		return self.vim.cursor

class Tab:
	def __init__(self):
		self.vim = vim.current.tabpage
		self.window = Window()
	
	def switch(self):
		if(vim.current.tabpage.number != self.tabpage.number):
			vim.command(":tab "+str(self.tabpage.number))

	def switch_to(self):
		self.switch()
		self.window.switch_to()

	def tabnum(self):
		return self.tab.vim.number
	def winnum(self):
		return self.tab.window.vim.number
	def bufnum(self):
		return self.tab.window.buffer.vim.number

class Link:
	def __init__(self):
		self.tab = Tab()

	def switch_to(self):
		self.tab.switch_to()
	
	def width(self):
		return int(vim.eval("winwidth('"+str(self.tab.winnum())+"')"))

	def height(self):
		return int(vim.eval("winheight('"+str(self.tab.winnum())+"')"))

	def refresh(self):
		vim.command(":redraw")
	
	def write(self, data, line=-1):
		self.tab.window.buffer.write(data, line)
	
	def clear(self):
		self.tab.window.buffer.clear()

