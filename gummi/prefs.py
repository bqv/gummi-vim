
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

WELCOME = """\\documentclass{article}
\\begin{document}

\\noindent\huge{Welcome to Gummi} \\\\
\\\\
\\large	{You are using the svn version.\\\\
	I welcome your suggestions at:\\\\
	http://code.google.com/p/gummi\\\\

\\end{document}"""
	

class prefs:
	
	def __init__(self, parent):
		self.parent = parent
		self.gconf_client = gconf.client_get_default()
		self.check_for_defaults()

	def create_gui(self):
		builder = gtk.Builder()	
		builder.add_from_file(self.parent.installdir + "/gui/prefs.xml")

		self.prefwindow = builder.get_object("prefwindow")
		self.box = builder.get_object("hbox1")
		self.notebook = builder.get_object("notebook1")
		self.textwrap_char = builder.get_object("textwrap_char")
		self.textwrap_word = builder.get_object("textwrap_word")
		self.textlines_display = builder.get_object("textlines_display")
		self.textlines_highlight = builder.get_object("textlines_highlight")
		self.box.pack_start(self.notebook, expand=False)
		
		self.textwrap_char.connect("toggled", self.run_wrapping_char, "textwrap char")
		self.textwrap_word.connect("toggled", self.run_wrapping_word, "textwrap word")
		self.textlines_display.connect("toggled", self.run_lines, "textlines display")
		self.textlines_highlight.connect("toggled", self.run_highlight, "textlines highlight")

		self.get_current_status()

		builder.connect_signals(self)
		self.prefwindow.show_all()


	def get_current_status(self):
		self.textwrap_char.set_active(1)
		if self.get_config_value("string", "text_wrapping") == "char":
			self.textwrap_char.set_active(1)
		if self.get_config_value("string", "text_wrapping") == "word":
			self.textwrap_char.set_active(1)
			self.textwrap_word.set_active(1)
		if self.get_config_value("string", "text_lines") == "True":
			self.textlines_display.set_active(1)
		if self.get_config_value("string", "text_highlight") == "True":
			self.textlines_highlight.set_active(1)


	def run_wrapping_char(self, widget, data=None):
		if widget.get_active() == False:
			self.textwrap_word.set_active(0)
			self.parent.editorpane.set_wrapping("None")
		else:
			self.parent.editorpane.set_wrapping("char")


	def run_wrapping_word(self, widget, data=None):
		if widget.get_active() == False:
			self.parent.editorpane.set_wrapping("char")
		if widget.get_active() == True:
			self.parent.editorpane.set_wrapping("word")


	def run_lines(self, widget, data=None):
		if widget.get_active() == False:
			self.parent.editorpane.editorview.set_show_line_numbers(False)
			self.gconf_client.set_string("/apps/gummi/text_lines", "False")
		else:
			self.parent.editorpane.editorview.set_show_line_numbers(True)
			self.gconf_client.set_string("/apps/gummi/text_lines", "True")


	def run_highlight(self, widget, data=None):
		if widget.get_active() == False:
			self.parent.editorpane.editorview.set_highlight_current_line(False)
			self.gconf_client.set_string("/apps/gummi/text_highlight", "False")
		else:
			self.parent.editorpane.editorview.set_highlight_current_line(True)
			self.gconf_client.set_string("/apps/gummi/text_highlight", "True")


	def get_config_value(self, type, item):
		if type == "string":
			configitem = self.gconf_client.get_string("/apps/gummi/" + item)
			return configitem
		if type == "list":
			configitem = self.gconf_client.get_string("/apps/gummi/" + item)
			return configitem


	def get_config_status(self, item):
		if self.gconf_client.get_string("/apps/gummi/" + item) == "True":
			return 1
		else:
			return 0
	

	def check_for_defaults(self):
		textwrapping = self.gconf_client.get_string("/apps/gummi/text_wrapping")
		if textwrapping is None:
			self.gconf_client.set_string("/apps/gummi/text_wrapping", "word")
		textlines = self.gconf_client.get_string("/apps/gummi/text_lines")
		if textlines is None:
			self.gconf_client.set_string("/apps/gummi/text_lines", "True")
		texthighlight = self.gconf_client.get_string("/apps/gummi/text_highlight")
		if texthighlight is None:
			self.gconf_client.set_string("/apps/gummi/text_highlight", "True")
		default = self.gconf_client.get_string("/apps/gummi/default-text")		
		if default is None:
			self.gconf_client.set_string("/apps/gummi/default-text", WELCOME)

