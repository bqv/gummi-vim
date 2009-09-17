
# --------------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <alexvandermey@gmail.com> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return -Alexander van der Mey
# --------------------------------------------------------------------------------

import gtk
import pango
import gtksourceview2
from datetime import datetime

import Preferences


class TexPane:

	def __init__(self, config):
		self.config = config
		self.editorbuffer = gtksourceview2.Buffer()
		self.manager = gtksourceview2.LanguageManager()
		self.language = self.manager.get_language("latex")
		self.editorbuffer.set_language(self.language)
		self.editorbuffer.set_highlight_matching_brackets(True)
		self.editorbuffer.set_highlight_syntax(True)
		self.editorviewer = gtksourceview2.View(self.editorbuffer)
		self.editorviewer.modify_font(pango.FontDescription("monospace 10"))

		self.editorviewer.set_show_line_numbers(config.get_value("bool", "tex_linenumbers"))
		self.editorviewer.set_highlight_current_line(config.get_value("bool", "tex_highlighting"))
		self.editorviewer.set_wrap_mode(self.grab_wrapmode())

		self.start_iter = None
		self.current_iter = None
		self.textchange = datetime.now()
		self.prevchange = datetime.now()
		self.check_text_change()
		
		self.editorviewer.connect("key-press-event", self.set_text_change,)
		self.editorbuffer.set_modified(False)

	def fill_buffer(self, text):
		self.editorviewer.set_sensitive(False)
		self.editorbuffer.set_text(text)
		self.editorbuffer.set_modified(False)
		self.editorviewer.set_sensitive(True)

	def grab_buffer(self):
		buff = self.editorviewer.get_buffer()
		self.editorviewer.set_sensitive(False)
		content = buff.get_text(buff.get_start_iter(), buff.get_end_iter())
		self.editorviewer.set_sensitive(True)
		buff.set_modified(False)
		return content

	def set_selection_textstyle(self, widget):
		try:	
			ins = self.editorbuffer.get_selection_bounds()[0]
			if widget.get_name() == "tool_bold":
				self.editorbuffer.insert(ins, "\\textbf{")
			if widget.get_name() == "tool_italic":
				self.editorbuffer.insert(ins, "\\textit{")
			if widget.get_name() == "tool_unline":
				self.editorbuffer.insert(ins, "\\underline{")
			end = self.editorbuffer.get_selection_bounds()[1]
			self.editorbuffer.insert(end, "}")
			self.textchange = datetime.now()
		except:	return

	def start_searchfunction(self):
		self.start_iter = self.editorbuffer.get_start_iter()
		self.current_iter = self.editorbuffer.get_iter_at_mark(self.editorbuffer.get_insert())

	def search_buffer(self, term, flags):
		if flags[0] is False: 
			try:
				ins, bound = gtksourceview2.iter_forward_search(self.current_iter, term, flags[1], limit=None)
				self.current_iter = bound			
			except:			
				return	
		else:	
			try:
				ins, bound = gtksourceview2.iter_backward_search(self.current_iter, term, flags[1], limit=None)
				self.current_iter = ins			
			except:
				return
		self.editorbuffer.place_cursor(ins)
		self.editorbuffer.select_range(ins, bound)
		self.editorviewer.scroll_to_iter(ins, 0)

	def grab_wrapmode(self):
		textwrap = self.config.get_value("bool", "tex_textwrapping")
		wordwrap = self.config.get_value("bool", "tex_wordwrapping")
		if textwrap is False:
			return gtk.WRAP_NONE
		if wordwrap is True:
			return gtk.WRAP_WORD
		else:
			return gtk.WRAP_CHAR

	def trigger_update(self):
		self.textchange = datetime.now()

	def set_text_change(self, widget, event):
		self.textchange = datetime.now()

	def check_text_change(self):	
		if self.prevchange != self.textchange:
			self.prevchange = self.textchange
			return True
		else:		
			return False

	def undo_change(self):
		if self.editorviewer.get_buffer().can_undo():
			self.editorviewer.get_buffer().undo()
			self.trigger_update()

	def redo_change(self):
		if self.editorviewer.get_buffer().can_redo():
			self.editorviewer.get_buffer().redo()
			self.trigger_update()


