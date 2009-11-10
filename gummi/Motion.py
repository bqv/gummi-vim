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
import subprocess
import traceback
import tempfile
import re


import Preferences


class Motion:

	def __init__(self, config, tex, preview, error, light, tempdir):
		self.config = config
		self.editorpane = tex
		self.previewpane = preview
		self.statuslight = light
		self.tempdir = tempdir

		self.texfile = None
		self.texname = None
		self.texpath = None
		self.tmpfile = None
		self.pdffile = None
		self.workfile = None
		self.status = 1
		self.laststate = None
		self.errormesg = re.compile(':[\d+]+:([^.]+)\.')
		self.errorline = re.compile(':([\d+]+):')

		# get the default typesetter (pdflatex) if the gconf 
		# value for some reason can't be fetched
		try: self.texcmd = self.config.get_string("tex_cmd")
		except: self.texcmd = Preferences.TYPESETTER

		self.editorviewer = self.editorpane.editorviewer
		self.editorbuffer = self.editorpane.editorbuffer
		self.errorbuffer = error.get_buffer()
		self.start_monitoring()

	def start_monitoring(self):
		glib.timeout_add(1000, self.update_preview)

	def create_environment(self, filename):
		self.texfile = filename
		self.texpath = os.path.dirname(self.texfile) + "/"
		if ".tex" in self.texfile:
			self.texname = os.path.basename(self.texfile)[:-4]
		else:
			self.texname = os.path.basename(self.texfile)
		self.workfile = tempfile.mkstemp(".tex")[1]
		self.pdffile = self.workfile[:-4] + ".pdf"
		print ("\nEnvironment created for: \nTEX: " + self.texfile +
		       "\nTMP: " + self.workfile + "\nPDF: " + self.pdffile + "\n")
		self.initial_preview()

	def initial_preview(self):
		self.update_workfile()
		self.update_pdffile()
		try:
			self.previewpane.set_pdffile(self.pdffile)
			self.previewpane.refresh_preview()
		except: self.previewpane.drawarea.hide(); return

	def export_pdffile(self):
		try: # export the pdf file if one exists
			export = self.texpath + self.texname + ".pdf"
			shutil.copy2(self.pdffile, export)
			os.chdir(self.texpath)
		except IOError: pass

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
		#self.status += 1
		#print self.status
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
			#mesgresult = self.errormesg.findall(self.output)
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




