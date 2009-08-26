
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


	def grab_wrapmode(self):
		textwrap = self.gconf_client.get_bool("/apps/gummi/tex_textwrapping")
		wordwrap = self.gconf_client.get_bool("/apps/gummi/tex_wordwrapping")
		print textwrap
		print wordwrap
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



