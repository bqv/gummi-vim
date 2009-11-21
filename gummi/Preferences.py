#!/usr/bin/python
# -*- encoding: utf-8 -*-

LICENSE="""
Copyright (c) 2009 Alexander van der Mey <alexvandermey@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import gtk
import gconf
import pango
import gobject

VERSION = "svn"
GCONFPATH = "/apps/gummi/"
UPDATEURL = "http://gummi.googlecode.com/svn/trunk/dev/latest"
DEFAULT_TEXT = """\documentclass{article}
\\begin{document}

\\begin{center}
\Huge{Welcome to Gummi} \\\\\\
\\\\
\\LARGE{You are using the """ + VERSION + """ version.\\\\
I welcome your suggestions at\\\\
http://gummi.midnightcoding.org}\\\\
\\end{center}

\\end{document}
"""

TEX_HIGHLIGHTING = True
TEX_LINENUMBERS = True
TEX_TEXTWRAPPING = True
TEX_WORDWRAPPING = True
AUTOSAVING = False
AUTOSAVE_TIMER = 600
TYPESETTER = "pdflatex"
RECENT_FILES = []
BIB_FILES = []


class Preferences:

	# TODO: Rewrite everything in this class

	def __init__(self, parent, path):
		self.core = parent
		self.path = path
		self.gconf_client = gconf.client_get_default()

	def get_default(self, key):
		if key == "tex_highlighting": return TEX_HIGHLIGHTING
		elif key == "tex_linenumbers": return TEX_LINENUMBERS
		elif key == "tex_textwrapping": return TEX_TEXTWRAPPING
		elif key == "tex_wordwrapping": return TEX_WORDWRAPPING
		elif key == "autosaving": return AUTOSAVING
		elif key == "autosave_timer": return AUTOSAVE_TIMER
		elif key == "tex_defaulttext": return DEFAULT_TEXT
		elif key == "recent_files": return RECENT_FILES
		elif key == "bib_files": return BIB_FILES
		elif key == "tex_cmd": return TYPESETTER
		else: return 1

	def get_bool(self,key):
		item = self.gconf_client.get(GCONFPATH + key)
		if item == None:
			default = self.get_default(key)
			self.gconf_client.set_bool(GCONFPATH + key, default)
			self.gconf_client.set_bool(GCONFPATH + key, default)
			return default
		else:
			return self.gconf_client.get_bool(GCONFPATH + key)

	def set_bool(self, key, value):
		self.gconf_client.set_bool(GCONFPATH + key, value)

	def get_string(self,key):
		item = self.gconf_client.get(GCONFPATH + key)
		if item == None:
			default = self.get_default(key)
			self.gconf_client.set_string(GCONFPATH + key, default)
			return default
		else:
			return self.gconf_client.get_string(GCONFPATH + key)

	def set_string(self, key, value):
		self.gconf_client.set_string(GCONFPATH + key, value)

	def get_int(self,key):
		item = self.gconf_client.get(GCONFPATH + key)
		if item == None:
			default = self.get_default(key)
			self.gconf_client.set_int(GCONFPATH + key, default)
			return default
		else:
			return self.gconf_client.get_int(GCONFPATH + key)

	def set_int(self, key, value):
		self.gconf_client.set_int(GCONFPATH + key, value)

	def get_list(self,key):
		item = self.gconf_client.get(GCONFPATH + key)
		if item == None:
			default = self.get_default(key)
			self.gconf_client.set_list(GCONFPATH + key, gconf.VALUE_STRING, default)
			return default
		else:
			return self.gconf_client.get_list(GCONFPATH + key, gconf.VALUE_STRING)

	def set_list(self, key, value):
		self.gconf_client.set_list(GCONFPATH + key, gconf.VALUE_STRING, value)

	def append_to_list(self, key, value):
		result = self.get_list(key)
		result.append(value)
		self.gconf_client.set_list(GCONFPATH + key, gconf.VALUE_STRING, result)

	def remove_from_list(self, key, value):
		result = self.get_list(key)
		del result[value]
		self.gconf_client.set_list(GCONFPATH + key, gconf.VALUE_STRING, result)


	def display_preferences(self):
		builder = gtk.Builder()
		builder.add_from_file(self.path + "/gui/prefs.glade")
		builder.connect_signals(self)

		self.editorpane = self.core.editorpane
		self.prefwindow = builder.get_object("prefwindow")
		self.prefwindow.set_transient_for(self.core.gui.mainwindow)
		self.notebook = builder.get_object("notebook1")

		self.button_textwrap = builder.get_object("button_textwrap")
		self.button_wordwrap = builder.get_object("button_wordwrap")
		self.button_linenumbers = builder.get_object("button_linenumbers")
		self.button_highlighting = builder.get_object("button_highlighting")
		self.check_autosave = builder.get_object("check_autosave")
		self.default_textfield = builder.get_object("default_textfield")
		self.typesetter = builder.get_object("combo_typesetter")

		typesetterstore = gtk.ListStore(gobject.TYPE_STRING)
		typesetterstore.append (["pdflatex"])
		typesetterstore.append (["xelatex"])
		cell = gtk.CellRendererText()
		self.typesetter.pack_start(cell, True)
		self.typesetter.add_attribute(cell, 'text',0)
		self.typesetter.set_model(typesetterstore)
		if self.get_string("tex_cmd") == "xelatex": self.typesetter.set_active(1)
		else: self.typesetter.set_active(0)
		autosave_timer = builder.get_object("autosave_time")
		autosave_timer.set_value(10)


		self.default_textfield.modify_font(pango.FontDescription("monospace 10"))
		self.default_buffer = self.default_textfield.get_buffer()
		self.default_buffer.set_text(self.get_string("tex_defaulttext"))

		self.check_current_setting(self.button_textwrap, "tex_textwrapping")
		self.check_current_setting(self.button_wordwrap, "tex_wordwrapping")
		self.check_current_setting(self.button_linenumbers, "tex_linenumbers")
		self.check_current_setting(self.button_highlighting, "tex_highlighting")
		self.check_current_setting(self.check_autosave, "check_autosave")

		self.button_textwrap.connect("toggled", self.toggle_button, "tex_textwrapping")
		self.button_wordwrap.connect("toggled", self.toggle_button, "tex_wordwrapping")
		self.button_linenumbers.connect("toggled", self.toggle_button, "tex_linenumbers")
		self.button_highlighting.connect("toggled", self.toggle_button, "tex_highlighting")
		self.check_autosave.connect("toggled", self.toggle_button, "autosaving")

		self.prefwindow.show_all()

	def check_current_setting(self, button, item):
		check = self.get_bool(item)
		if check is True: button.set_active(True)
		elif check is False: button.set_active(False)

	def toggle_button(self, widget, data=None):
		if widget.get_active(): self.set_bool(data, True)
		else: self.set_bool(data, False)
		if self.button_textwrap.get_active() is False:
			self.button_wordwrap.set_active(False)
			self.button_wordwrap.set_sensitive(False)
		if self.button_textwrap.get_active() is True:
			self.button_wordwrap.set_sensitive(True)
		self.engage(widget, data)

	def autosave_timer_change(self, event):
		newvalue = int(event.get_value()) * 60
		self.set_int("autosave_timer", newvalue)

	def engage(self, widget, data):
		if data == "tex_textwrapping":
			if widget.get_active():
				self.core.editorpane.editorviewer.set_wrap_mode(gtk.WRAP_CHAR)
			else:
				self.core.editorpane.editorviewer.set_wrap_mode(gtk.WRAP_NONE)
		elif data == "tex_wordwrapping":
			if widget.get_active():
				self.core.editorpane.editorviewer.set_wrap_mode(gtk.WRAP_WORD)
			else:
				self.core.editorpane.editorviewer.set_wrap_mode(gtk.WRAP_CHAR)
		elif data == "tex_linenumbers":
			if widget.get_active():
				self.core.editorpane.editorviewer.set_show_line_numbers(True)
			else:
				self.core.editorpane.editorviewer.set_show_line_numbers(False)
		elif data == "tex_highlighting":
			if widget.get_active():
				self.core.editorpane.editorviewer.set_highlight_current_line(True)
			else:
				self.core.editorpane.editorviewer.set_highlight_current_line(False)

	def on_combo_typesetter_changed(self, item, data=None):
		if item.get_active_text() == "xelatex": self.set_string("tex_cmd", "xelatex")
		elif item.get_active_text() == "pdflatex": self.set_string("tex_cmd", "pdflatex")

	def on_prefs_close_clicked(self, widget, data=None):
		if self.notebook.get_current_page() == 2:
			newtext = self.default_buffer.get_text(self.default_buffer.get_start_iter(), self.default_buffer.get_end_iter())
			self.set_string("tex_defaulttext", newtext)
		self.prefwindow.destroy()

	def on_prefs_reset_clicked(self, widget, data=None):
		if self.notebook.get_current_page() == 0:
			self.set_bool("tex_linenumbers", self.get_default("tex_linenumbers"))
			self.set_bool("tex_highlighting", self.get_default("tex_highlighting"))
			self.set_bool("tex_textwrapping", self.get_default("tex_textwrapping"))
			self.set_bool("tex_wordwrapping", self.get_default("tex_wordwrapping"))
			self.check_current_setting(self.button_textwrap, "tex_textwrapping")
			self.check_current_setting(self.button_wordwrap, "tex_wordwrapping")
			self.check_current_setting(self.button_linenumbers, "tex_linenumbers")
			self.check_current_setting(self.button_highlighting, "tex_highlighting")
		elif self.notebook.get_current_page() == 1:
			self.set_bool("autosaving", self.get_default("autosaving"))
			self.check_current_setting(self.check_autosave, "autosaving")
			self.set_int("autosave_timer", self.get_default("autosave_timer"))
		elif self.notebook.get_current_page() == 2:
			self.set_string("tex_defaulttext", DEFAULT_TEXT)
			self.default_buffer.set_text(self.get_string("tex_defaulttext"))
		elif self.notebook.get_current_page() == 3:
			self.typesetter.set_active(0)



