#!/usr/bin/env python

# Copyright (c) 2013 John Sullivan
# Copyright (c) 2013 Other contributers as noted in the CONTRIBUTERS file
#
# This file is part of superzippy
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import zipsite
import superconfig
import module_locator
import os.path

zipsite.addsitedir(
	os.path.abspath(os.path.join(
		module_locator.module_path(), "site-packages"
	)),
	prepend_mode = True
)

if len(sys.argv) == 2 and sys.argv[1] == "--superzippy-debug-console":
	# Pulled from http://stackoverflow.com/a/5597918/1989056
	import readline
	import code
	vars = globals().copy()
	vars.update(locals())
	shell = code.InteractiveConsole(vars)
	shell.interact()

# Entry point is expected to be in the form module:function
load_module, run_func = superconfig.entry_point.split(":")

module = __import__(load_module, fromlist = [run_func])

getattr(module, run_func)()
