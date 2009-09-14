
# --------------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <alexvandermey@gmail.com> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return -Alexander van der Mey
# --------------------------------------------------------------------------------

import gtk
import gtksourceview2
import pango
import gconf
import gobject
from datetime import datetime


class texpane:

	def __init__(self):

		self.bufferS = gtksourceview2.Buffer()
		self.manager = gtksourceview2.LanguageManager()
		self.language = self.manager.get_language("latex")
		self.bufferS.set_language(self.language)
		self.bufferS.set_highlight_matching_brackets(True)
		self.bufferS.set_highlight_syntax(True)
		self.editorview = gtksourceview2.View(self.bufferS)

		self.gconf_client = gconf.client_get_default()
		self.editorview.set_show_line_numbers(self.gconf_client.get_bool("/apps/gummi/tex_linenumbers"))
		self.editorview.set_highlight_current_line(self.gconf_client.get_bool("/apps/gummi/tex_highlighting"))
		self.editorview.set_wrap_mode(self.grab_wrapmode())
		
		self.editorview.modify_font(pango.FontDescription("monospace 10"))
		
		self.textchange = datetime.now()
		self.prevchange = datetime.now()
		self.check_text_change()

		self.editorview.connect("key-press-event", self.set_text_change,)
		self.bufferS.set_modified(False)

		self.pdffile = None
		self.workfile = None
		self.filename = None
		self.status = 1


	def insert_package(self, package, current_iter):
		pkgspace = "\\begin{document}"		
		start_iter = self.bufferS.get_start_iter()
		begin_iter, end = gtksourceview2.iter_forward_search(start_iter, pkgspace, flags=0, limit=None)
		pkgsearchstr = "{" + package + "}"
		if gtksourceview2.iter_forward_search(start_iter, pkgsearchstr, flags=0, limit=begin_iter):
			return
		else:
			self.bufferS.insert(begin_iter, "\\usepackage{" + package + "}\n")


	def set_selection_bold(self, widget):
		try:		
			ins = self.bufferS.get_selection_bounds()[0]
			if widget.get_name() == "tool_style_bold":
				self.bufferS.insert(ins, "\\textbf{")
				end = self.bufferS.get_selection_bounds()[1]
				self.bufferS.insert(end, "}")
				self.textchange = datetime.now()
		except:	return	

	def set_selection_italic(self, widget):
		try:		
			ins = self.bufferS.get_selection_bounds()[0]
			if widget.get_name() == "tool_style_italic":
				self.bufferS.insert(ins, "\\textit{")
				end = self.bufferS.get_selection_bounds()[1]
				self.bufferS.insert(end, "}")
				self.textchange = datetime.now()
		except: return

	def set_selection_unline(self, widget):
		try:		
			ins = self.bufferS.get_selection_bounds()[0]
			if widget.get_name() == "tool_style_unline":
				self.bufferS.insert(ins, "\\underline{")
				end = self.bufferS.get_selection_bounds()[1]
				self.bufferS.insert(end, "}")
				self.textchange = datetime.now()
		except: return


	def grab_wrapmode(self):
		textwrap = self.gconf_client.get_bool("/apps/gummi/tex_textwrapping")
		wordwrap = self.gconf_client.get_bool("/apps/gummi/tex_wordwrapping")
		if textwrap is False:
			return gtk.WRAP_NONE
		if wordwrap is True:
			return gtk.WRAP_WORD
		else:
			return gtk.WRAP_CHAR


	def set_text_change(self, widget, event):
		#self.bufferS.set_modified(True)
		self.textchange = datetime.now()


	def check_text_change(self):	
		if self.prevchange != self.textchange:
			self.prevchange = self.textchange
			return True
		else:		
			return False



