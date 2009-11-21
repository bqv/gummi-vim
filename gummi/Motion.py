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

import os
import glib
import shutil
import pango
import subprocess
import traceback
import tempfile
import re

import Preferences

class Motion:

	def __init__(self, config, editor, preview, builder):

		self.config = config
		self.editorpane = editor
		self.previewpane = preview

		self.status = 1
		self.laststate = None

		try: self.texcmd = self.config.get_string("tex_cmd")
		except: self.texcmd = Preferences.TYPESETTER

		self.errormesg = re.compile(':[\d+]+:([^.]+)\.')
		self.errorline = re.compile(':([\d+]+):')

		self.statuslight = builder.get_object("tool_statuslight")
		self.statusbar = builder.get_object("statusbar")
		self.statusbar_cid = self.statusbar.get_context_id("Gummi")
		self.errorfield = builder.get_object("errorfield")
		self.errorfield.modify_font(pango.FontDescription("monospace 8"))
		self.errorbuffer = self.errorfield.get_buffer()

		self.editorviewer = self.editorpane.editorviewer
		self.editorbuffer = self.editorpane.editorbuffer
		#self.start_updatepreview()

	def start_updatepreview(self):
		glib.timeout_add_seconds(1, self.update_preview)

	def update_envfiles(self, envfile):
		self.tempdir = envfile[0]
		self.filename = envfile[1]
		self.texpath = envfile[2]
		self.workfile = envfile[3]
		self.pdffile = envfile[4]

	def initial_preview(self):
		self.update_workfile()
		self.update_pdffile()
		try:
			self.previewpane.set_pdffile(self.pdffile)
			self.previewpane.refresh_preview()
			self.start_updatepreview()
		except: self.previewpane.drawarea.hide(); return

	def update_workfile(self):
		try:
			# these two lines make the program hang in certain situations
			#self.editorpane.editorview.set_sensitive(False)
			buff = self.editorpane.editorviewer.get_buffer()
			start_iter, end_iter = buff.get_start_iter(), buff.get_end_iter()
			content = buff.get_text(start_iter, end_iter)
			#self.editorpane.editorview.set_sensitive(True)
			tmpmake = open(self.workfile, "w")
			tmpmake.write(content)
			tmpmake.close()
			self.editorviewer.grab_focus() #editorpane regrabs focus
		except:
			print traceback.print_exc()

	def update_auxfile(self):
		auxupdate = subprocess.Popen(self.texcmd + ' --draftmode -interaction=nonstopmode --output-directory="%s" "%s"' % (self.tempdir, self.workfile), shell=True, stdin=None, stdout=subprocess.PIPE, stderr=None)
		output = auxupdate.communicate()[0]
		#output to a textbuffer soon
		auxupdate.wait()

	def update_pdffile(self):
		try:
			pdfmaker = subprocess.Popen(self.texcmd + \
					' -file-line-error \
					-halt-on-error \
					--output-directory="%s" "%s"' \
					% (self.tempdir, self.workfile), 
					shell=True, cwd=self.texpath, close_fds=True, \
					stdin=None, stdout = subprocess.PIPE, stderr=None )
			self.output = pdfmaker.communicate()[0]
			pdfmaker.wait()
			try: os.close(3) # very important
			except: pass # do not remove
			self.errorbuffer.set_text(self.output)
			if pdfmaker.returncode:
				self.statuslight.set_stock_id("gtk-no")
			else:
				self.statuslight.set_stock_id("gtk-yes")
		except: print traceback.print_exc()
		return pdfmaker.returncode

	def update_errortags(self, errorstate):
		if errorstate is 1 and "Fatal error" in self.output:
			lineresult = self.errorline.findall(self.output)
			if lineresult == []: # end tag error
				lineresult.insert(0, self.editorbuffer.get_line_count())
			mesgresult = self.errormesg.findall(self.output)
			self.editorpane.apply_errortags(int(lineresult[0]))	
		elif errorstate is 0 and errorstate < self.laststate:
			self.editorpane.apply_errortags(None)
		else: pass
		self.laststate = errorstate

	def update_preview(self):
		try:
			if self.previewpane and self.editorpane.check_buffer_changed():
				self.editorpane.check_buffer_changed()
				self.update_workfile()
				retcode = self.update_pdffile()
				self.update_errortags(retcode)
				self.previewpane.refresh_preview()
		except:
			print traceback.print_exc()
		return True 




