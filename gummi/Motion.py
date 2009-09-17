
# --------------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <alexvandermey@gmail.com> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return -Alexander van der Mey
# --------------------------------------------------------------------------------

import os
import sys
import gtk
import thread
import subprocess
import traceback
import tempfile
import gobject
import time

import Preferences


class Motion:
	
	def __init__(self, tex, pdf, error, light):
		self.editorpane = tex
		self.previewpane = pdf
		self.statuslight = light

		self.texfile = None		
		self.tmpfile = None
		self.pdffile = None
		self.status = 1

		self.editorviewer = self.editorpane.editorviewer
		self.editorbuffer = self.editorpane.editorbuffer
		self.errorbuffer = error.get_buffer()

		gobject.threads_init()
		gtk.gdk.threads_init()
		self.start_monitoring()

	def start_monitoring(self):
		self.refresh = thread.start_new_thread(self.update_preview, ())

	def create_environment(self, filename):	
		self.texfile = filename
		self.texpath = os.path.dirname(self.texfile) + "/"	
		if ".tex" in self.texfile:
			self.texname = os.path.basename(self.texfile)[:-4] 
		else:
			self.texname = os.path.basename(self.texfile)
		fd, path = tempfile.mkstemp(".tex")
		self.workfile = os.readlink("/proc/self/fd/%d" % fd)
		self.pdffile = self.texpath + self.texname + ".pdf"
		print ("\nEnvironment created for: \nTEX: " + self.texfile + 
		       "\nTMP: " + self.workfile + "\nPDF: " + self.pdffile + "\n")
		self.initial_preview()

	def initial_preview(self):
		self.update_workfile()
		self.update_pdffile()
		try:		
			self.previewpane.create_preview(self.pdffile)
			self.previewpane.refresh_preview()
		except:
			self.previewpane.drawarea.hide()

	def update_workfile(self):
		# these two lines make the program hang in certain situations, no clue why	
		#self.editorpane.editorview.set_sensitive(False)
		self.buffer = self.editorpane.editorviewer.get_buffer()
		start_iter, end_iter = self.buffer.get_start_iter(), self.buffer.get_end_iter()
		content = self.buffer.get_text(start_iter, end_iter)
		#self.editorpane.editorview.set_sensitive(True)
		tmpmake = open(self.workfile, "w")
		tmpmake.write(content)
		tmpmake.close()
		self.editorviewer.grab_focus() #editorpane regrabs focus

	def update_pdffile(self):	
		os.chdir(self.texpath)
		pdfmaker = subprocess.Popen('pdflatex -interaction=nonstopmode -jobname="%s" "%s"' % (self.texname, self.workfile), shell=True, stdin=None, stdout = subprocess.PIPE, stderr=None)
		output = pdfmaker.communicate()[0]
		pdfmaker.wait()
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
				if self.previewpane and self.status == 1 and self.editorpane.check_text_change():
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



