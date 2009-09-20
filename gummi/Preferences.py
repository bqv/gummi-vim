
# --------------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <alexvandermey@gmail.com> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return -Alexander van der Mey
# --------------------------------------------------------------------------------

import gtk
import gconf
import pango

VERSION = "svn"
GCONFPATH = "/apps/gummi/"
UPDATEURL = "http://gummi.googlecode.com/svn/trunk/dev/latest"
DEFAULT_TEXT = """\\documentclass{article}
\\begin{document}

\\noindent\huge{Welcome to Gummi} \\\\
\\\\
\\large	{You are using the """ + VERSION + """ version.\\\\
	I welcome your suggestions at:\\\\
	http://code.google.com/p/gummi}\\\\
\\\\
\\end{document}"""

TEX_HIGHLIGHTING = True
TEX_LINENUMBERS = True
TEX_TEXTWRAPPING = True
TEX_WORDWRAPPING = True


class Preferences:

	# TODO: Rewrite everything in this class

	def __init__(self, parent):
		self.parent = parent
		self.gconf_client = gconf.client_get_default()

	def get_default(self, key):
		if key is "tex_highlighting": return TEX_HIGHLIGHTING
		elif key is "tex_linenumbers": return TEX_LINENUMBERS
		elif key is "tex_textwrapping": return TEX_TEXTWRAPPING
		elif key is "tex_wordwrapping": return TEX_WORDWRAPPING
		elif key is "tex_defaulttext": return DEFAULT_TEXT
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

	def display_preferences(self):
		builder = gtk.Builder()	
		builder.add_from_file(self.parent.CWD + "/gui/prefs.xml")
		builder.connect_signals(self)

		self.prefwindow = builder.get_object("prefwindow")
		self.notebook = builder.get_object("notebook1")

		self.button_textwrap = builder.get_object("button_textwrap")
		self.button_wordwrap = builder.get_object("button_wordwrap")
		self.button_linenumbers = builder.get_object("button_linenumbers")
		self.button_highlighting = builder.get_object("button_highlighting")
		self.default_textfield = builder.get_object("default_textfield")

		self.default_textfield.modify_font(pango.FontDescription("monospace 10"))
		self.default_buffer = self.default_textfield.get_buffer()
		self.default_buffer.set_text(self.get_string("tex_defaulttext"))

		self.check_current_setting(self.button_textwrap, "tex_textwrapping")
		self.check_current_setting(self.button_wordwrap, "tex_wordwrapping")
		self.check_current_setting(self.button_linenumbers, "tex_linenumbers")
		self.check_current_setting(self.button_highlighting, "tex_highlighting")

		self.button_textwrap.connect("toggled", self.toggle_button, "tex_textwrapping")
		self.button_wordwrap.connect("toggled", self.toggle_button, "tex_wordwrapping")
		self.button_linenumbers.connect("toggled", self.toggle_button, "tex_linenumbers")
		self.button_highlighting.connect("toggled", self.toggle_button, "tex_highlighting")

		self.prefwindow.set_transient_for(self.parent.mainwindow)
		self.prefwindow.show_all()

	def check_current_setting(self, button, item):
		check = self.get_bool(item)
		if check is True:
			button.set_active(True)
		if check is False:
			button.set_active(False)

	def toggle_button(self, widget, data=None):
		if widget.get_active() == False:
			self.set_bool(data, False)
		else:
			self.set_bool(data, True)
		if self.button_textwrap.get_active() is False:
			self.button_wordwrap.set_active(False)
			self.button_wordwrap.set_sensitive(False)
		if self.button_textwrap.get_active() is True:
			self.button_wordwrap.set_sensitive(True)
		self.engage(widget, data)

	def engage(self, widget, data):
		if data is "tex_textwrapping":
			if widget.get_active() == False:
				self.parent.editorpane.editorviewer.set_wrap_mode(gtk.WRAP_NONE)
			else:
				self.parent.editorpane.editorviewer.set_wrap_mode(gtk.WRAP_CHAR)
		if data is "tex_wordwrapping":
			if widget.get_active() == False:
				self.parent.editorpane.editorviewer.set_wrap_mode(gtk.WRAP_CHAR)
			else:
				self.parent.editorpane.editorviewer.set_wrap_mode(gtk.WRAP_WORD)
		if data is "tex_linenumbers":
			if widget.get_active() == False:
				self.parent.editorpane.editorviewer.set_show_line_numbers(False)
			else:
				self.parent.editorpane.editorviewer.set_show_line_numbers(True)
		if data is "tex_highlighting":
			if widget.get_active() == False:
				self.parent.editorpane.editorviewer.set_highlight_current_line(False)
			else:
				self.parent.editorpane.editorviewer.set_highlight_current_line(True)


	def on_prefs_close_clicked(self, widget, data=None):
		if self.notebook.get_current_page() is 2:
			newtext = self.default_buffer.get_text(self.default_buffer.get_start_iter(), self.default_buffer.get_end_iter())
			self.set_string("tex_defaulttext", newtext)	
		self.prefwindow.destroy()

	def on_prefs_reset_clicked(self, widget, data=None):
		if self.notebook.get_current_page() is 0:
			self.set_bool("tex_linenumbers", self.get_default("tex_linenumbers"))
			self.set_bool("tex_highlighting", self.get_default("tex_highlighting"))
			self.set_bool("tex_textwrapping", self.get_default("tex_textwrapping"))
			self.set_bool("tex_wordwrapping", self.get_default("tex_wordwrapping"))		
			self.check_current_setting(self.button_textwrap, "tex_textwrapping")
			self.check_current_setting(self.button_wordwrap, "tex_wordwrapping")
			self.check_current_setting(self.button_linenumbers, "tex_linenumbers")
			self.check_current_setting(self.button_highlighting, "tex_highlighting")		
		if self.notebook.get_current_page() is 1:
			return
		if self.notebook.get_current_page() is 2:
			self.set_string("tex_defaulttext", DEFAULT_TEXT)
			self.default_buffer.set_text(self.get_string("tex_defaulttext"))


