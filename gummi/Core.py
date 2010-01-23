#!/usr/bin/python
# -*- encoding: utf-8 -*-

# Copyright (c) 2009 Alexander van der Mey <alexvandermey@gmail.com>

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import gtk
import os
import sys
import traceback

import GummiGUI
import Preferences
import Motion
import TexPane
import PreviewPane
import IOFunctions
import Biblio


class Core:
	
	def __init__(self):

		# environment: 
		self.path = path
		self.tempdir = os.environ.get("TMPDIR", "/tmp")
		self.filename = None

		# graphical components:
		self.builder = gtk.Builder()
		self.builder.add_from_file(path + "/gui/gummi.glade")
		statusbar = self.builder.get_object("statusbar")

		# class instances:
		config = Preferences.Preferences()
		self.editorpane = TexPane.TexPane(config)
		self.previewpane = PreviewPane.PreviewPane(self.builder)
		self.motion = Motion.Motion(config, self.editorpane, self.previewpane, self.builder)
		self.iofunc = IOFunctions.IOFunctions(config, statusbar, self.editorpane, self.motion)
		self.biblio = Biblio.Biblio(self.editorpane, self.motion)
		self.gui = GummiGUI.MainGUI(self, config, self.iofunc, self.biblio)

		# setup document to load:
		if len(sys.argv) > 1:
			self.filename = sys.argv[1]
			self.iofunc.load_file(self.filename)
		else:
			self.filename = None
			self.iofunc.load_default_text()
		self.iofunc.make_environment(self.filename)

		# gui main:
		self.gui.main()



if __name__ == "__main__":
	path = sys.path[0]
else: 
	path = os.path.dirname(__file__)
try:
	instance = Core()
except:
	print traceback.print_exc()
