
# --------------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <alexvandermey@gmail.com> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return -Alexander van der Mey
# --------------------------------------------------------------------------------

import os
import gtk
import gobject
import time
import thread
import tempfile 
import subprocess
import traceback


class motion:

	def __init__(self, parent):
		self.parent = parent
		self.previewpane = self.parent.previewpane
		self.editorpane = self.parent.editorpane

		self.status = 1
		self.workfile = None
		self.pdffile = None
		self.texfile = None

		gobject.threads_init()
		gtk.gdk.threads_init()

		self.start_monitoring()

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
		print "\nEnvironment created for " + self.texfile + "\nWorkfile is " + self.workfile + "\nPdffile is " + self.pdffile + "\n"

	def initial_preview(self):
		self.update_workfile()
		self.update_pdffile()
		self.previewpane.create_previewpane(self.pdffile, self.parent.pdfdrawarea)
		self.previewpane.refresh_previewpane()

	def start_monitoring(self):
		self.refresh = thread.start_new_thread(self.start_preview_monitor, ())

	def update_pdffile(self):	
		os.chdir(self.texpath)
		output = tempfile.NamedTemporaryFile(mode='w+b')
		pdfmaker = subprocess.Popen('pdflatex -interaction=nonstopmode -jobname="%s" "%s"' % (self.texname, self.workfile), shell=True, stdout=output)
		pdfmaker.wait()
		
	def update_workfile(self):
		buff = self.editorpane.editorview.get_buffer()	
		# these two lines make the program hang in certain situations, look into it later. 		
		#self.editorpane.editorview.set_sensitive(False)
		text = buff.get_text(buff.get_start_iter(), buff.get_end_iter())
		#self.editorpane.editorview.set_sensitive(True)
		tmpmake = open(self.workfile, "w")
		tmpmake.write(text)
		tmpmake.close()
		self.editorpane.editorview.grab_focus() #editorpane regrabs focus

	def start_preview_monitor(self):
		while True:
			try:
				if self.previewpane and self.status == 1 and self.parent.editorpane.check_text_change():
					gtk.gdk.threads_enter
					self.parent.editorpane.check_text_change()
					self.update_workfile()
					self.update_pdffile()
					self.previewpane.refresh_previewpane()			
					gtk.gdk.threads_leave
			except:
				print "something is wrong with the refresh thread"
				print traceback.print_exc()
	
			time.sleep(1.0)
		


