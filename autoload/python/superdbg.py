#!/usr/bin/env python

# Ability to load local scripts/modules
import os
import inspect
import sys
directory = os.path.dirname(inspect.getfile(inspect.currentframe()))
sys.path.append(directory)

import dbg

