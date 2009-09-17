
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


class Preferences:

	# TODO: Rewrite everything in this class

	def __init__(self, parent):
		self.parent = parent
		self.gconf_client = gconf.client_get_default()
	
		# replace with schema soon
		firstrun = self.gconf_client.get_string(GCONFPATH + "set_defaults")
		if firstrun is None:
			self.set_defaults()

	def test(self):
		print "test werkt"

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
		self.default_buffer.set_text(self.get_value("string", "tex_defaulttext"))

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

	def get_value(self, type, item):
		if type == "string":
			configitem = self.gconf_client.get_string(GCONFPATH + item)
			return configitem
		if type == "list":
			configitem = self.gconf_client.get_list(GCONFPATH + item)
			return configitem
		if type == "bool":		
			configitem = self.gconf_client.get_bool(GCONFPATH + item)		
			return configitem

	def set_config_bool(self, item, value):
		self.gconf_client.set_bool(GCONFPATH + item, value)

	def set_config_string(self, item, value):
		self.gconf_client.set_string(GCONFPATH + item, value)

	def set_config_list(self, item, value):
		self.gconf_client.set_list(GCONFPATH + item, value)

	def check_current_setting(self, button, item):
		check = self.get_value("bool", item)
		if check is True:
			button.set_active(True)
		if check is False:
			button.set_active(False)


	def toggle_button(self, widget, data=None):
		if widget.get_active() == False:
			self.set_config_bool(data, False)
		else:
			self.set_config_bool(data, True)
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
			self.set_config_string("tex_defaulttext", newtext)	
		self.prefwindow.destroy()

	def on_prefs_reset_clicked(self, widget, data=None):
		if self.notebook.get_current_page() is 0:
			self.set_config_bool("tex_linenumbers", True)
			self.set_config_bool("tex_highlighting", True)
			self.set_config_bool("tex_textwrapping", True)
			self.set_config_bool("tex_wordwrapping", True)		
			self.check_current_setting(self.button_textwrap, "tex_textwrapping")
			self.check_current_setting(self.button_wordwrap, "tex_wordwrapping")
			self.check_current_setting(self.button_linenumbers, "tex_linenumbers")
			self.check_current_setting(self.button_highlighting, "tex_highlighting")		
		if self.notebook.get_current_page() is 1:
			return
		if self.notebook.get_current_page() is 2:
			self.set_config_string("tex_defaulttext", DEFAULT_TEXT)
			self.default_buffer.set_text(self.get_value("string", "tex_defaulttext"))

	def set_defaults(self):

		tex_linenumbers = self.gconf_client.get_bool(GCONFPATH + "tex_linenumbers")
		self.gconf_client.set_bool(GCONFPATH + "tex_linenumbers", True)

		tex_highlighting = self.gconf_client.get_bool(GCONFPATH + "tex_highlighting")
		self.gconf_client.set_bool(GCONFPATH + "tex_highlighting", True)

		tex_textwrapping = self.gconf_client.get_bool(GCONFPATH + "tex_textwrapping")
		self.gconf_client.set_bool(GCONFPATH + "tex_textwrapping", True)

		tex_wordwrapping = self.gconf_client.get_bool(GCONFPATH + "tex_wordwrapping")
		self.gconf_client.set_bool(GCONFPATH + "tex_wordwrapping", True)

		tex_defaulttext = self.gconf_client.get_string(GCONFPATH + "tex_defaulttext")
		self.gconf_client.set_string(GCONFPATH + "tex_defaulttext", DEFAULT_TEXT)

		self.gconf_client.set_string(GCONFPATH + "set_defaults", "OK")





