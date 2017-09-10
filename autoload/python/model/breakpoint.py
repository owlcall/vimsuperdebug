#!/usr/bin/env python
#
# model_breakpoints.py 
# Copyright (c) 2017 owl
#

class Breakpoint:
	container = {}
	def __init__(self, source, line):
		self.source = source
		self.line = line
		self.set = False

class Model:
	container = {}

	@classmethod
	def add(cls, source, line):
		if not source in cls.container:
			cls.container[source] = {}
		if not line in cls.container[source]:
			cls.container[source][line] = Breakpoint(source, line)

	@classmethod
	def delete(cls, source, line):
		if not source in cls.container:
			return
		if not line in cls.container[source]:
			return
		cls.container[source].pop(line, None)

	@classmethod
	def unset_all(cls):
		for _, group in cls.container.iteritems():
			for _, item in group.iteritems():
				item.set = False
