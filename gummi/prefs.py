
# --------------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <alexvandermey@gmail.com> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return -Alexander van der Mey
# --------------------------------------------------------------------------------

import os
import sys
import gtk
import gconf
import pango

DEFAULT = """\\documentclass{article}
\\begin{document}

\\noindent\huge{Welcome to Gummi} \\\\
\\\\
\\large	{You are using the svn version.\\\\
	I welcome your suggestions at:\\\\
	http://code.google.com/p/gummi\\\\
\\\\
\\end{document}"""

GCONFPATH = "/apps/gummi/"

class prefs:
	
	def __init__(self, parent):
		self.parent = parent
		self.gconf_client = gconf.client_get_default()		
		
		firstrun = self.gconf_client.get_string(GCONFPATH + "set_defaults")
		if firstrun is None:
			self.set_defaults()


	def get_config_value(self, type, item):
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


	def create_gui(self):
		builder = gtk.Builder()	
		builder.add_from_file(self.parent.installdir + "/gui/prefs.xml")
		builder.connect_signals(self)

		self.prefwindow = builder.get_object("prefwindow")
		self.prefwindow.set_transient_for(self.parent.mainwindow)

		self.box = builder.get_object("hbox1")
		self.notebook = builder.get_object("notebook1")
		self.box.pack_start(self.notebook, expand=False)

		self.button_textwrap = builder.get_object("button_textwrap")
		self.button_wordwrap = builder.get_object("button_wordwrap")
		self.button_linenumbers = builder.get_object("button_linenumbers")
		self.button_highlighting = builder.get_object("button_highlighting")
		self.default_textfield = builder.get_object("default_textfield")

		self.default_textfield.modify_font(pango.FontDescription("monospace 10"))


		self.check_current_setting(self.button_textwrap, "tex_textwrapping")
		self.check_current_setting(self.button_wordwrap, "tex_wordwrapping")
		self.check_current_setting(self.button_linenumbers, "tex_linenumbers")
		self.check_current_setting(self.button_highlighting, "tex_highlighting")

		self.button_textwrap.connect("toggled", self.toggle_button, "tex_textwrapping")
		self.button_wordwrap.connect("toggled", self.toggle_button, "tex_wordwrapping")
		self.button_linenumbers.connect("toggled", self.toggle_button, "tex_linenumbers")
		self.button_highlighting.connect("toggled", self.toggle_button, "tex_highlighting")
		
		self.prefwindow.show_all()

	def check_current_setting(self, button, item):
		check = self.get_config_value("bool", item)
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
				self.parent.editorpane.editorview.set_wrap_mode(gtk.WRAP_NONE)
			else:
				self.parent.editorpane.editorview.set_wrap_mode(gtk.WRAP_CHAR)
		if data is "tex_wordwrapping":
			if widget.get_active() == False:
				self.parent.editorpane.editorview.set_wrap_mode(gtk.WRAP_CHAR)
			else:
				self.parent.editorpane.editorview.set_wrap_mode(gtk.WRAP_WORD)
		if data is "tex_linenumbers":
			if widget.get_active() == False:
				self.parent.editorpane.editorview.set_show_line_numbers(False)
			else:
				self.parent.editorpane.editorview.set_show_line_numbers(True)
		if data is "tex_highlighting":
			if widget.get_active() == False:
				self.parent.editorpane.editorview.set_highlight_current_line(False)
			else:
				self.parent.editorpane.editorview.set_highlight_current_line(True)


	def on_prefs_close_clicked(self, widget, data=None):
		self.prefwindow.destroy()

	def on_prefs_reset_clicked(self, widget, data=None):
		print "reset"	


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
		self.gconf_client.set_string(GCONFPATH + "tex_defaulttext", DEFAULT)

		self.gconf_client.set_string(GCONFPATH + "set_defaults", "OK")


