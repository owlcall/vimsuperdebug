#!/usr/bin/env python
#
# breakpoint.py 
# Copyright (c) 2017 owl
#

import os,re
import vim
import view

VBP_NAME = "sdebug_bp"

def cerr(data):
	sys.stderr.write(data)

class View:
	# Map of {path:{line, boolean}}
	breakpoints = {}

	@classmethod
	def sign(add,path,line):
		try:
			cmd = 'silent sign '+'place' if add else 'unplace'
			if add: 
				vim.command(cmd+' %i line=%i name=%s file=%s'%(line,line,VBP_NAME,path))
			else:
				vim.command(cmd+' %i file=%s'%(line,source))
		except vim.error as err:
			print(err)


	@classmethod
	def initialize(c):
		vim.command('silent sign define %s text=BP texthl=Search'%(VBP_NAME))
		#linehl=Search
	
	# def update_breakpoints(c):
		# signs = vim.eval('SDebugSignlist()')

		# signs = signs.split("Signs for")
		# print(signs)

		# import re
		# rex = re.compile(r'Signs\sfor\s.+\:\n.*?', re.MULTILINE)
		
	@classmethod
	def update_current(c, model):
		path = vim.eval('expand("%:p")')
		if not os.path.exists(path): return

		text = vim.eval('SDebugSignlistCurrent()')
		if not text:
			cerr("no signs to load")
			return

		# Parse existing signs to ensure we don't add duplicates
		import re
		rex = re.compile(r'line=(\d+)\s+id=(\d+)\s+name=(\S+)', re.MULTILINE)

		signlist = {}
		for match in rex.finditer(text):
			line, id, name = match.groups()
			if name == VBP_NAME:
				signlist[line] = True

		# Attempt to load breakpoint signs into this file
		# Duplicate breakpoint signs are ignored
		for src,lines in model.container.iteritems():
			if os.path.basename(path) != src and src != path: continue
			if os.path.basename(path) == src: src = path
			# Update each breakpoint line in current file as a BP sign
			for ln, bp in lines.iteritems():
				if str(ln) in signlist: continue
				# Must provide full path file as argument, otherwise errors
				vim.command('silent sign place %i line=%i name=%s file=%s'%(ln,ln,VBP_NAME,path))

	@classmethod
	def line_info(c):
		source = vim.eval("expand('%:p')")
		line = vim.current.window.cursor[0]
		modified = vim.current.buffer.options['modified']
		return (source,line,modified)
	
	@classmethod
	def add(c, source, line):
		if vim.current.buffer.options['modified']:
			cerr("error setting breakpoint; buffer has unsaved changes.")
			return
		try:
			cmd = 'silent sign '
			vim.command(cmd+'place %i line=%i name=%s file=%s'%(line,line,VBP_NAME,source))
		except vim.error as err:
			print(err)

	@classmethod
	def remove(c, source, line):
		if vim.current.buffer.options['modified']:
			cerr("error setting breakpoint; buffer has unsaved changes.")
			return
		cmd = 'silent sign '
		vim.command(cmd+'unplace %i file=%s'%(line,source))

	@classmethod
	def clear(c):
		#TODO implement clearing of all breakpoints
		pass

