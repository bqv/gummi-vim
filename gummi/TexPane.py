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

import gtk
import pango
import locale
import gtksourceview2
from datetime import datetime

import Formatting

START = "START"
END = "END"
CURRENT = "CURRENT"
BEGIN = "\\begin{document}"
PACKAGES = "\\usepackage{"

class TexPane:

	def __init__(self, config):
		self.editorbuffer = gtksourceview2.Buffer()
		self.editortags = self.editorbuffer.get_tag_table()
		self.manager = gtksourceview2.LanguageManager()
		self.searchresults = []
		self.errortag = gtk.TextTag()
		self.searchtag = gtk.TextTag()
		self.configure_texpane(config)

		self.textchange = datetime.now()
		self.prevchange = datetime.now()
		self.check_buffer_changed()

		self.editorviewer.connect("key-press-event", self.set_buffer_changed,)
		self.editorbuffer.set_modified(False)


	def configure_texpane(self, config):
		"""Configures the gtksourceview (editor) widget"""
		self.language = self.manager.get_language("latex")
		self.editorbuffer.set_language(self.language)
		self.editorbuffer.set_highlight_matching_brackets(True)
		self.editorbuffer.set_highlight_syntax(True)
		self.editorviewer = gtksourceview2.View(self.editorbuffer)
		self.editorviewer.modify_font \
			(pango.FontDescription(config.get_value("editor", "font")))
		self.editorviewer.set_show_line_numbers( \
						bool(config.get_value("view", "line_numbers")))
		self.editorviewer.set_highlight_current_line( \
						bool(config.get_value("view", "highlighting")))
		textwrap = config.get_value("view", "textwrapping")
		wordwrap = config.get_value("view", "wordwrapping")
		mode = self.grab_wrapmode(textwrap, wordwrap)
		self.editorviewer.set_wrap_mode(mode)
		self.errortag.set_property('background', 'red')
		self.errortag.set_property('foreground', 'white')
		self.searchtag.set_property('background', 'yellow')


	def fill_buffer(self, newcontent):
		"""Clears the buffer and writes new not-undoable data into it"""
		self.editorbuffer.begin_user_action()
		self.editorbuffer.set_text("")		
		self.editorbuffer.begin_not_undoable_action()
		start = self.editorbuffer.get_start_iter()
		self.editorviewer.set_sensitive(False)		
		self.editorbuffer.insert(start, newcontent)
		self.editorbuffer.set_modified(False)
		self.editorviewer.set_sensitive(True)
		self.editorbuffer.end_not_undoable_action()
		self.editorbuffer.end_user_action()

	def grab_buffer(self):
		"""Grabs content of the buffer and returns it for writing to file."""
		buff = self.editorviewer.get_buffer()
		self.editorviewer.set_sensitive(False)
		start = self.get_iterator(START)
		end = self.get_iterator(END)
		content = buff.get_text(start, end)
		self.editorviewer.set_sensitive(True)
		buff.set_modified(False)
		return content

	def decode_text(self, filename):
		loadfile = open(filename, "r")
		content = loadfile.read()
		encoding = locale.getdefaultlocale()[1]
		try: decoded_content = content.decode(encoding)
		except (UnicodeError, TypeError):
			try: decoded_content = content.decode("iso-8859-1", 'replace')
			except (UnicodeError, TypeError):
				decoded_content = content.decode("ascii", 'replace')
		loadfile.close()
		return decoded_content

	def encode_text(self, text):
		encoding = locale.getdefaultlocale()[1]
		try: encoded_content = text.encode(encoding)
		except (UnicodeError, TypeError):
			try: encoded_content = text.encode("iso-8859-1", 'replace')
			except (UnicodeError, TypeError):
				encoded_content = text.encode("ascii", 'replace')
		return encoded_content

	def get_iterator(self, tag, search=1):
		"""Returns a buffer iterator object for a known position in the buffer
			or a custom searchstring. The optional argument search determines
			whether iter is placed in front or after the find result"""	
		if tag == "START":
			bufferiter = self.editorbuffer.get_start_iter()
		elif tag == "END":
			bufferiter = self.editorbuffer.get_end_iter()
		elif tag == "CURRENT":
			bufferiter = self.editorbuffer.get_iter_at_mark(self.editorbuffer.get_insert())
		else:
			if search == 0:
				enditer = self.editorbuffer.get_end_iter()
				bufferiter = gtksourceview2.iter_backward_search \
							(enditer, tag, flags=0, limit=None)[0]
			else:
				startiter = self.editorbuffer.get_start_iter()
				bufferiter = gtksourceview2.iter_forward_search \
						(startiter, tag, flags=0, limit=None)[0]
		return bufferiter

	def insert_package(self, package):
		start_iter = self.get_iterator(START)
		end_iter = self.get_iterator(BEGIN, 1)
		pkgsearchstr = "{" + package + "}"
		pkginsertstr = "\\usepackage{" + package + "}\n"
		if gtksourceview2.iter_forward_search \
		(start_iter, pkgsearchstr, flags=0, limit=end_iter):
			return
		else:
			self.editorbuffer.begin_not_undoable_action()
			self.editorbuffer.insert(end_iter, pkginsertstr)
			self.editorbuffer.end_not_undoable_action()
		self.set_buffer_changed()

	def insert_bib(self, package):
		start_iter = self.get_iterator(BEGIN)
		end_iter = self.get_iterator("\\end{document}", 0)
		searchstr = "\\bibliography{"
		insertstr = "\\bibliography{" + package + "}{}\n"
		stylestr = "\\bibliographystyle{plain}\n"
		if gtksourceview2.iter_forward_search(start_iter, searchstr, flags=0, limit=end_iter):
			return
		else:
			self.editorbuffer.begin_not_undoable_action()
			self.editorbuffer.insert(end_iter, insertstr + stylestr)
			self.editorbuffer.end_not_undoable_action()
		self.set_buffer_changed()

	def set_selection_textstyle(self, widget):
		Formatting.Formatting(widget, self.editorbuffer)
		self.set_buffer_changed()

	def apply_errortags(self, errorline):
		try: #remove the tag from the table if it is in there
			self.editortags.remove(self.errortag)
		except ValueError: pass
		if errorline is not None: #re-add the tag if an error was found
			self.editortags.add(self.errortag)
			start = self.editorbuffer.get_iter_at_line(errorline-1)
			end = self.editorbuffer.get_iter_at_line(errorline)
			self.editorbuffer.apply_tag(self.errortag, start, end)

	# TODO merge function with apply_errortags (multiple error results soon)
	def apply_searchtags(self, searchresults):
		try:
			self.searchresultiters = []
			self.searchposition = 0
			self.editortags.remove(self.searchtag)			
		except ValueError: pass
		self.editortags.add(self.searchtag)
		for result in searchresults:
			self.searchresultiters.append(result)
			self.editorbuffer.apply_tag(self.searchtag, result[0], result[1])

	def jumpto_searchresult(self, direction):
		try: 
			if self.searchposition + direction < 0:
				return False
			ins, bnd = self.searchresultiters[self.searchposition + direction]
			self.editorbuffer.place_cursor(ins)
			self.searchposition = self.searchposition + direction
		except IndexError: pass

	def start_search(self, term, backwards, matchcase=0):
		self.searchresults = []
		if matchcase is False:
			matchcase = (gtksourceview2.SEARCH_CASE_INSENSITIVE)
		if backwards is True:
			self.searchresults = self.search_buffer_backward(term, matchcase)
		else:
			self.searchresults = self.search_buffer_forward(term, matchcase)
		self.apply_searchtags(self.searchresults)
		try:
			ins, bound = self.searchresults[0]
			self.editorbuffer.place_cursor(ins)
			#self.editorbuffer.select_range(ins, bound)
			self.editorviewer.scroll_to_iter(ins, 0)
		except IndexError: pass #no searchresults

	def search_buffer_forward(self, term, matchcase):
		result_list = []
		begin = self.get_iterator(CURRENT)
		while True:
			result = gtksourceview2.iter_forward_search \
						(begin, term, matchcase, limit=None)
			if result:
				result_list.append((result[0], result[1]))
				begin = result[1]
			else:
				break
		return result_list

	def search_buffer_backward(self, term, matchcase):
		result_list = []
		begin = self.get_iterator(CURRENT)
		while True:
			result = gtksourceview2.iter_backward_search \
						(begin, term, matchcase, limit=None)
			if result:
				result_list.append((result[0], result[1]))
				begin = result[0]
			else:
				break
		return result_list

	def grab_wrapmode(self, textwrap, wordwrap):
		if textwrap is False:
			return gtk.WRAP_NONE
		elif wordwrap is True:
			return gtk.WRAP_WORD
		else:
			return gtk.WRAP_CHAR

	def set_buffer_changed(self, *args):
		self.textchange = datetime.now()

	def check_buffer_changed(self):
		if self.prevchange != self.textchange:
			self.prevchange = self.textchange
			return True
		else:
			return False

	def undo_change(self):
		if self.editorviewer.get_buffer().can_undo():
			self.editorviewer.get_buffer().undo()
			self.set_buffer_changed()

	def redo_change(self):
		if self.editorviewer.get_buffer().can_redo():
			self.editorviewer.get_buffer().redo()
			self.set_buffer_changed()


