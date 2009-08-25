
# --------------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <alexvandermey@gmail.com> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return -Alexander van der Mey
# --------------------------------------------------------------------------------

import gtk
import gtksourceview2
import pango
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

		#todo: replace with gconf values from prefs
		self.editorview.set_show_line_numbers(True)
		self.editorview.set_highlight_current_line(True)
		self.editorview.set_wrap_mode(gtk.WRAP_WORD)
		
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


	def set_wrapping(self, wrapmode):
		if wrapmode == "None":
			self.editorview.set_wrap_mode(gtk.WRAP_NONE)
		elif wrapmode == "char":
			self.editorview.set_wrap_mode(gtk.WRAP_CHAR)
		else:
			self.editorview.set_wrap_mode(gtk.WRAP_WORD)


	def set_text_change(self, widget, event):
		#self.bufferS.set_modified(True)
		self.textchange = datetime.now()


	def check_text_change(self):	
		if self.prevchange != self.textchange:
			self.prevchange = self.textchange
			return True
		else:		
			return False



