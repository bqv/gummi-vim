
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
import subprocess
import shutil
import pango


class Biblio:
	"""Handles the inclusion of .bib files and the GUI elements involved"""

	def __init__(self, config, editorpane, motion, builder):
		self.config = config
		self.editorpane = editorpane		
		self.motion = motion
		self.biblist = None

		self.mainwindow = builder.get_object("mainwindow")
		self.treeview = builder.get_object("bib_treeview")
		self.treelist = builder.get_object("bib_treelist")
		self.biboutput = builder.get_object("bibtex_output")
		self.biboutput.modify_font(pango.FontDescription("monospace 9"))

		textrenderer = gtk.CellRendererText()
		column = gtk.TreeViewColumn("Name", textrenderer, text=1)
		self.treeview.append_column(column)
		self.parse_listdata()

	def parse_listdata(self):
		self.biblist = self.config.get_list("bib_files")
		i = 0
		for row in self.biblist: #int id, name displayed
			self.treelist.append([i, row])
			i = i + 1


	def refresh_listdata(self):
		self.treelist.clear() #remove all rows
		self.parse_listdata()


	def select_listdata(self, column):
		selection = self.treeview.get_selection()
		myiter = selection.get_selected()[1]
		value = self.treelist.get_value(myiter, column)
		return value


	def add_bibliography(self):
		self.biblist = self.config.get_list("bib_files")
		bibfile = None
		chooser = gtk.FileChooserDialog("Open File...", self.mainwindow,
								gtk.FILE_CHOOSER_ACTION_OPEN,
								(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
								gtk.STOCK_OPEN, gtk.RESPONSE_OK))
		bibfilter = gtk.FileFilter()
		bibfilter.set_name('Bibtex files')
		bibfilter.add_pattern("*.bib")
		chooser.add_filter(bibfilter)
		
		response = chooser.run()
		if response == gtk.RESPONSE_CANCEL: return
		if response == gtk.RESPONSE_OK: 
			bibfile = chooser.get_filename()
			if bibfile not in self.biblist:
				self.config.append_to_list("bib_files", bibfile)		
				self.refresh_listdata()
		chooser.destroy()
	

	def del_bibliography(self):
		value = self.select_listdata(0)
		self.config.remove_from_list("bib_files", int(value))
		self.refresh_listdata()


	def setup_bibliography(self):
		self.editorpane.insert_package("cite")
		bibfile = self.select_listdata(1)
		tempdir = os.environ.get("TMPDIR", "/tmp")
		bibname = os.path.basename(bibfile)[:-4]
		shutil.copy2(bibfile, tempdir + "/" + bibname + ".bib")
		self.editorpane.insert_bib(bibname)
		self.compile_bibliography()

	def compile_bibliography(self):
		self.motion.update_workfile()
		workfile = self.motion.workfile[:-4]
		self.motion.update_auxfile()
		tempdir = os.environ.get("TMPDIR", "/tmp")
		cwd = os.getcwd()
		os.chdir(tempdir)
		bibcompile = subprocess.Popen('bibtex "%s"' % (workfile), shell=True, stdin=None, stdout=subprocess.PIPE, stderr=None)
		bibcompile.wait()
		os.chdir(cwd)
		output = bibcompile.communicate()[0]
		self.biboutput.get_buffer().set_text(output)
		self.editorpane.text_changed()






		



