#!/usr/bin/env python
#
# model_breakpoints.py 
# Copyright (c) 2017 owl
#

class Breakpoint:
	def __init__(self, source, line):
		self.source = source
		self.line = line
		self.set = False
		self.id = -1

class Model:
	container = {}

	@classmethod
	def get(cls, source, line):
		if not source in cls.container or not line in cls.container[source]:
			return None
		return cls.container[source][line]

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
