
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
import gtk
import thread
import shutil
import subprocess
import traceback
import tempfile
import gobject
import time

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

		try: self.texcmd = self.config.get_string("tex_cmd")
		except: self.texcmd = Preferences.TYPESETTER

		self.editorviewer = self.editorpane.editorviewer
		self.editorbuffer = self.editorpane.editorbuffer
		self.errorbuffer = error.get_buffer()

		gobject.threads_init()
		gtk.gdk.threads_init()
		self.start_monitoring()

	def start_monitoring(self):
		previewthread = thread.start_new_thread(self.update_preview, ())

	def create_environment(self, filename):
		self.texfile = filename
		self.texpath = os.path.dirname(self.texfile) + "/"
		if ".tex" in self.texfile:
			self.texname = os.path.basename(self.texfile)[:-4]
		else:
			self.texname = os.path.basename(self.texfile)
		fd = tempfile.mkstemp(".tex")[0]
		self.workfile = os.readlink("/proc/self/fd/%d" % fd)
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
		except Exception as e:
			print 'oeps:', e
			self.previewpane.drawarea.hide()

	def export_pdffile(self):
		try: # export the pdf file if one exists
			export = self.texpath + self.texname + ".pdf"
			shutil.copy2(self.pdffile, export)
			os.chdir(self.texpath)
		except IOError: pass

	def update_workfile(self):
		try:
			# these two lines make the program hang in certain situations, no clue why
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
		#os.chdir(self.texpath)
		pdfmaker = subprocess.Popen(self.texcmd + ' -interaction=nonstopmode --output-directory="%s" "%s"' % (self.tempdir, self.workfile), shell=True, stdin=None, stdout = subprocess.PIPE, stderr=None)
		output = pdfmaker.communicate()[0]
		pdfmaker.wait()
		try: os.close(3)
		except: pass
		self.errorbuffer.set_text(output)
		err1 = "Fatal error"
		err2 = "Emergency stop"
		err3 = "LaTeX Error"
		if err1 in output or err2 in output or err3 in output:
			self.statuslight.set_stock_id("gtk-no")
		else:
			self.statuslight.set_stock_id("gtk-yes")


	def update_preview(self):
		while True:
			try:
				if self.previewpane and self.status and self.editorpane.check_text_change():
					gtk.gdk.threads_enter
					self.editorpane.check_text_change()
					self.update_workfile()
					self.update_pdffile()
					self.previewpane.refresh_preview()
					gtk.gdk.threads_leave
			except:
				print "something is wrong with the refresh thread"
				print traceback.print_exc()
			time.sleep(1.0)



