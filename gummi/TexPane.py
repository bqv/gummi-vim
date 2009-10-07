
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
import pango
import gtksourceview2
from datetime import datetime

import Formatting


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

		self.editorviewer.set_show_line_numbers(config.get_bool("tex_linenumbers"))
		self.editorviewer.set_highlight_current_line(config.get_bool("tex_highlighting"))
		self.editorviewer.set_wrap_mode(self.grab_wrapmode())

		self.start_iter = None
		self.current_iter = None
		self.textchange = datetime.now()
		self.prevchange = datetime.now()
		self.check_text_change()
		
		self.editorviewer.connect("key-press-event", self.set_text_change,)
		self.editorbuffer.set_modified(False)

	def fill_buffer(self, newcontent):
		# will output a sourceview warning if (new content = current content)
		self.editorbuffer.set_text("")
		self.editorbuffer.begin_not_undoable_action()
		self.editorviewer.set_sensitive(False)
		start = self.editorbuffer.get_start_iter()
		self.editorbuffer.insert(start, newcontent)		
		self.editorbuffer.set_modified(False)		
		self.editorviewer.set_sensitive(True)
		self.editorbuffer.end_not_undoable_action()

	def grab_buffer(self):
		buff = self.editorviewer.get_buffer()
		self.editorviewer.set_sensitive(False)
		content = buff.get_text(buff.get_start_iter(), buff.get_end_iter())
		self.editorviewer.set_sensitive(True)
		buff.set_modified(False)
		return content

	def insert_package(self, package):
		pkgspace = "\\begin{document}"		
		start_iter = self.editorbuffer.get_start_iter()
		begin_iter = gtksourceview2.iter_forward_search(start_iter, pkgspace, flags=0, limit=None)[0]
		pkgsearchstr = "{" + package + "}"
		if gtksourceview2.iter_forward_search(start_iter, pkgsearchstr, flags=0, limit=begin_iter):
			return
		else:
			self.editorbuffer.begin_not_undoable_action()
			self.editorbuffer.insert(begin_iter, "\\usepackage{" + package + "}\n")
			self.editorbuffer.end_not_undoable_action()
		self.buffer_modified()

	def insert_bib(self, package):
		pkgspace = "\\end{document}"	
		end_iter = self.editorbuffer.get_end_iter()
		begin_iter = gtksourceview2.iter_backward_search(end_iter, pkgspace, flags=0, limit=None)[0]
		pkgsearchstr = "\\bibliography{"
		aa = self.editorbuffer.get_start_iter()
		bb = self.editorbuffer.get_end_iter()
		if gtksourceview2.iter_forward_search(aa, pkgsearchstr, flags=0, limit=bb):
			return
		else:
			self.editorbuffer.begin_not_undoable_action()
			self.editorbuffer.insert(begin_iter, "\\bibliography{" + package + "}{}\n" + "\\bibliographystyle{plain}\n")
			self.editorbuffer.end_not_undoable_action()	
		self.text_changed()


	def set_selection_textstyle(self, widget):
		Formatting.Formatting(widget, self.editorbuffer)		
		self.text_changed()

	def get_current_position(self):
		return self.editorbuffer.get_iter_at_mark(self.editorbuffer.get_insert())


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
		textwrap = self.config.get_bool("tex_textwrapping")
		wordwrap = self.config.get_bool("tex_wordwrapping")
		if textwrap is False:
			return gtk.WRAP_NONE
		if wordwrap is True:
			return gtk.WRAP_WORD
		else:
			return gtk.WRAP_CHAR

	def buffer_modified(self):
		self.textchange = datetime.now()

	def set_text_change(self, widget, event):
		self.textchange = datetime.now()

	def text_changed(self):
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
			self.buffer_modified()

	def redo_change(self):
		if self.editorviewer.get_buffer().can_redo():
			self.editorviewer.get_buffer().redo()
			self.buffer_modified()


