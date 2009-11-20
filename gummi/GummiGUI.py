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

import os
import sys
import gtk
import traceback

import TexPane
import PreviewPane
import Importer
import Motion
import Biblio
import Preferences
import UpdateCheck
import Template


class GummiGUI:

	def __init__(self, config, path):
		
		self.config = config

		self.filename = None
		self.exitinterrupt = False
		self.path = path

		builder = gtk.Builder()
		builder.add_from_file(self.path + "/gui/gummi.glade")
		self.builder = builder

		self.mainwindow = builder.get_object("mainwindow")
		self.toolbar = builder.get_object("toolbar")
		self.mainnotebook = builder.get_object("main_notebook")
		self.editorscroll = builder.get_object("editor_scroll")
		self.drawarea = builder.get_object("preview_drawarea")
		self.preview_toolbar = builder.get_object("preview_toolbar")

		self.searchwindow = builder.get_object("searchwindow")
		self.searchentry = builder.get_object("searchentry")
		self.backwards = builder.get_object("toggle_backwards")
		self.matchcase = builder.get_object("toggle_matchcase")
		
		self.recent1 = builder.get_object("menu_recent1")
		self.recent2 = builder.get_object("menu_recent2")
		self.recent3 = builder.get_object("menu_recent3")
		self.hpaned = builder.get_object("hpaned")

		self.menu_statusbar = builder.get_object("menu_statusbar")
		self.menu_statusbar.set_active(True)
		self.menu_toolbar = builder.get_object("menu_toolbar")
		self.menu_toolbar.set_active(True)
		self.menu_hlayout = builder.get_object("menu_hlayout")
		self.menu_vlayout = builder.get_object("menu_vlayout")

		self.box_image = builder.get_object("box_image")
		self.box_table = builder.get_object("box_table")
		self.box_matrix = builder.get_object("box_matrix")
		self.image_pane = builder.get_object("image_pane")
		self.table_pane = builder.get_object("table_pane")
		self.matrix_pane = builder.get_object("matrix_pane")

		self.tempdir = os.environ.get("TMPDIR", "/tmp")

		mainwidth = self.mainwindow.get_size()[0]
		self.hpaned.set_position(mainwidth/2)

		self.editorpane = TexPane.TexPane(self.config)
		self.previewpane = PreviewPane.PreviewPane(self.builder)
		self.importer = Importer.Importer(self.editorpane, builder)
		self.motion = Motion.Motion(self.config, self.editorpane, self.previewpane, self.builder, self.tempdir)
		self.editorscroll.add(self.editorpane.editorviewer)
		self.biblio = Biblio.Biblio(self.config, self.editorpane, self.motion, builder)

		builder.connect_signals(self) #split signals?
		self.create_initial_document()
		self.mainwindow.show_all()
		gtk.main()

	def create_initial_document(self):
		if len(sys.argv) > 1:
			self.filename = sys.argv[1]
			self.load_file(self.filename)
		else:
			self.filename = None
			self.editorpane.fill_buffer(self.config.get_string("tex_defaulttext"))
			self.motion.create_environment(self.filename)
			os.chdir(os.environ['HOME'])
		self.setup_recentfiles()

	def set_window_title(self, filename):
		self.mainwindow.set_title \
					(os.path.basename(filename) + " - Gummi")

	def on_menu_new_activate(self, menuitem, data=None):
		if self.check_for_save(): self.on_menu_save_activate(None, None)
		self.editorpane.fill_buffer(self.config.get_string("tex_defaulttext"))
		self.editorpane.editorbuffer.set_modified(False)
		self.filename = None
		self.motion.create_environment(self.filename)

	def on_menu_template_activate(self, menuitem, data=None):
		self.template_doc = Template.Template(self.builder, self.path)

	def on_menu_open_activate(self, menuitem, data=None):
		if os.getcwd() == self.tempdir:
			os.chdir(os.environ['HOME'])
		if self.check_for_save(): self.on_menu_save_activate(None, None)
		filename = self.get_open_filename()
		if filename: self.load_file(filename)

	def on_menu_save_activate(self, menuitem, data=None):
		if os.getcwd() == self.tempdir:
			os.chdir(os.environ['HOME'])
		if self.filename is None:
			filename = self.get_save_filename()
			if filename: self.write_file(filename)
		if os.path.dirname(self.filename) == self.tempdir:
			filename = self.get_save_filename()
			if filename: self.write_file(filename)
		else: self.write_file(None)

	def on_menu_saveas_activate(self, menuitem, data=None):
		if os.getcwd() == self.tempdir:
			os.chdir(os.environ['HOME'])
		self.filename = self.get_save_filename()
		if self.filename: self.write_file(self.filename)
		#self.motion.create_environment(self.filename)

	def on_menu_undo_activate(self, menuitem, data=None):
		self.editorpane.undo_change()

	def on_menu_redo_activate(self, menuitem, data=None):
		self.editorpane.redo_change()

	def on_menu_cut_activate(self, menuitem, data=None):
		buff = self.editorpane.editorviewer.get_buffer()
		buff.cut_clipboard (gtk.clipboard_get(), True)
		self.editorpane.set_buffer_changed()

	def on_menu_copy_activate(self, menuitem, data=None):
		buff = self.editorpane.editorviewer.get_buffer()
		buff.copy_clipboard (gtk.clipboard_get())

	def on_menu_paste_activate(self, menuitem, data=None):
		buff = self.editorpane.editorviewer.get_buffer()
		buff.paste_clipboard (gtk.clipboard_get(), None, True)
		self.editorpane.set_buffer_changed()

	def on_menu_delete_activate(self, menuitem, data=None):
		buff = self.editorpane.editorviewer.get_buffer()
		buff.delete_selection (False, True)

	def on_menu_selectall_activate(self, menuitem, data=None):
		buff = self.editorpane.editorviewer.get_buffer()
		buff.select_range(buff.get_start_iter(),buff.get_end_iter())

	def on_menu_find_activate(self, menuitem, data=None):
		self.editorpane.start_searchfunction()
		self.searchentry.set_text("")
		self.searchwindow.show()

	def on_menu_fullscreen_toggled(self, menuitem, data=None):
		if menuitem.get_active():
			self.mainwindow.fullscreen()
		else:
			self.mainwindow.unfullscreen()

	def on_menu_toolbar_toggled(self, menuitem, data=None):
		if menuitem.get_active():
			self.toolbar.show()
		else:
			self.toolbar.hide()
		pass

	def on_menu_statusbar_toggled(self, menuitem, data=None):
		if menuitem.get_active():
			self.motion.statusbar.show()
		else:
			self.motion.statusbar.hide()

	def on_button_template_ok_clicked(self, button, data=None):
		template = self.template_doc.get_template()
		if template is not None:
			self.editorpane.fill_buffer(template)
			self.filename = None
			self.motion.create_environment(self.tempdir + "/gummi-new")
			self.template_doc.templatewindow.hide()
		else: pass

	def on_button_template_cancel_clicked(self, button, data=None):
		self.template_doc.templatewindow.hide()
		return True

	def on_button_searchwindow_close_clicked(self, button, data=None):
		self.searchwindow.hide()
		return True

	def on_button_searchwindow_find_clicked(self, button, data=None):
		term = self.searchentry.get_text()
		backwards = self.backwards.get_active()
		matchcase = self.matchcase.get_active()
		#flags = self.editorpane.get_search_flags(backwards, matchcase)
		self.editorpane.search_buffer(term, backwards, matchcase)

	def on_import_tabs_switch_page(self, notebook, page, page_num):
		newactive = notebook.get_nth_page(page_num).get_name()
		self.box_image.foreach(lambda x:self.box_image.remove(x))
		self.box_table.foreach(lambda x:self.box_table.remove(x))
		self.box_matrix.foreach(lambda x:self.box_matrix.remove(x))
		if newactive == "box_image":
			self.box_image.add(self.image_pane)
		elif newactive == "box_table":
			self.box_table.add(self.table_pane)
		elif newactive == "box_matrix":
			self.box_matrix.add(self.matrix_pane)

	def on_button_imagepane_apply_clicked(self, button, data=None):
		self.importer.insert_image()

	def on_button_tablepane_apply_clicked(self, button, data=None):
		self.importer.insert_table()

	def on_button_matrixpane_apply_clicked(self, button, data=None):
		self.importer.insert_matrix()

	def on_image_file_activate(self, button, event, data=None):
		self.importer.prepare_image()

	def on_menu_bibupdate_activate(self, menuitem, data=None):
		self.biblio.compile_bibliography()

	def on_menu_preferences_activate(self, menuitem, data=None):
		self.config.display_preferences()

	def on_menu_update_activate(self, menuitem, data=None):
		update = UpdateCheck.UpdateCheck()

	def on_menu_about_activate(self, menuitem, data=None):
		authors = ["Alexander van der Mey\n<alexvandermey@gmail.com>\n\n"
					"Contributors:\n"
					"Thomas van der Burgt <thomas@thvdburgt.nl>\n"
					"Cameron Grout <camerongrout@gmail.com>\n"]				
		artwork = ["Template icon set from:\nhttp://www.fatcow.com/free-icons/"]
		about_dialog = gtk.AboutDialog()
		about_dialog.set_transient_for(self.mainwindow)
		about_dialog.set_destroy_with_parent(True)
		about_dialog.set_name("Gummi")
		about_dialog.set_license(Preferences.LICENSE)
		about_dialog.set_version(Preferences.VERSION)
		about_dialog.set_copyright("Copyright \xc2\xa9 2009 Alexander van der Mey")
		about_dialog.set_website("http://gummi.midnightcoding.org")
		about_dialog.set_comments("Simple LaTeX Editor for GTK+ users")
		about_dialog.set_authors(authors)
		about_dialog.set_artists(artwork)
		about_dialog.set_logo_icon_name	 (gtk.STOCK_EDIT)
		# callbacks for destroying the dialog
		def close(dialog, response, editor):
			editor.about_dialog = None
			dialog.destroy()
		def delete_event(dialog, event, editor):
			editor.about_dialog = None
			return True
		about_dialog.connect("response", close, self)
		about_dialog.connect("delete-event", delete_event, self)
		self.about_dialog = about_dialog
		about_dialog.show()


	def on_tool_bold_activate(self, button, data=None):
		self.editorpane.set_selection_textstyle(button)

	#redundant, but oh well..
	def on_tool_italic_activate(self, button, data=None):
		self.editorpane.set_selection_textstyle(button)

	def on_tool_unline_activate(self, button, data=None):
		self.editorpane.set_selection_textstyle(button)

	def on_tool_left_activate(self, button, data=None):
		self.editorpane.set_selection_textstyle(button)

	def on_tool_center_activate(self, button, data=None):
		self.editorpane.set_selection_textstyle(button)

	def on_tool_right_activate(self, button, data=None):
		self.editorpane.set_selection_textstyle(button)

	def on_button_pageback_clicked(self, button, data=None):
		self.previewpane.jump_to_prevpage()

	def on_button_pageforward_clicked(self, button, data=None):
		self.previewpane.jump_to_nextpage()

	def on_button_zoomin_clicked(self, button, data=None):
		self.previewpane.zoom_in_pane()

	def on_button_zoomout_clicked(self, button, data=None):
		self.previewpane.zoom_out_pane()

	def on_button_bestfit_toggled(self, button, data=None):
		if button.get_active() == False:
			self.previewpane.set_bestfitmode(False)
		else:
			self.previewpane.set_bestfitmode(True)

	def on_button_bibadd_clicked(self, button, data=None):
		self.biblio.add_bibliography()

	def on_button_bibdel_clicked(self, button, data=None):
		self.biblio.del_bibliography()

	def on_button_bibapply_clicked(self, button, data=None):
		self.biblio.setup_bibliography()
		self.mainnotebook.set_current_page(0)

	def setup_recentfiles(self):
		self.check_recentfile(0, self.recent1)
		self.check_recentfile(1, self.recent2)
		self.check_recentfile(2, self.recent3)

	def check_recentfile(self, i, widget):
		recents = self.config.get_list("recent_files")
		try:
			entry = os.path.basename(recents[i])
			widget.get_children()[0].set_label(str(i+1) + ". " + entry)
			widget.show()
		except IndexError: widget.hide()

	def on_menu_recent_activate(self, widget, data=None):
		recents = self.config.get_list("recent_files")
		widget = widget.get_name()
		if widget == "menu_recent1": self.load_recentfile(recents[0])
		if widget == "menu_recent2": self.load_recentfile(recents[1])
		if widget == "menu_recent3": self.load_recentfile(recents[2])

	def add_recentfile(self, filename):
		recents = self.config.get_list("recent_files")
		if filename not in recents:
			recents.insert(0, filename)
			if len(recents) > 3:
				del recents[3]
			self.config.set_list("recent_files", recents)
			self.setup_recentfiles()

	def load_recentfile(self, filename):
		self.check_for_save()
		self.load_file(filename)

	def set_file_filters(self, dialog):
		plainfilter = gtk.FileFilter()
		plainfilter.set_name('Text files')
		plainfilter.add_mime_type("text/plain")
		dialog.add_filter(plainfilter)

		latexfilter = gtk.FileFilter()
		latexfilter.set_name('LaTeX files')
		latexfilter.add_pattern('*.tex')
		dialog.add_filter(latexfilter)
		dialog.set_filter(plainfilter)

	def get_open_filename(self):
		filename = None
		chooser = gtk.FileChooserDialog("Open File...", self.mainwindow,
										gtk.FILE_CHOOSER_ACTION_OPEN,
										(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
										gtk.STOCK_OPEN, gtk.RESPONSE_OK))
		self.set_file_filters(chooser)

		response = chooser.run()
		if response == gtk.RESPONSE_OK: filename = chooser.get_filename()
		chooser.destroy()
		return filename

	def get_save_filename(self):
		filename = None
		chooser = gtk.FileChooserDialog("Save File...", self.mainwindow,
										gtk.FILE_CHOOSER_ACTION_SAVE,
										(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
										gtk.STOCK_SAVE, gtk.RESPONSE_OK))
		self.set_file_filters(chooser)
		response = chooser.run()
		if response == gtk.RESPONSE_CANCEL:
			self.exitinterrupt = True
		if response == gtk.RESPONSE_OK:
			filename = chooser.get_filename()
			if not ".tex" in filename[-4:]:
				filename = filename + ".tex"
			chooser.destroy()
			self.motion.create_environment(filename)
		chooser.destroy()
		return filename

	def check_for_save(self):
		ret = False
		if self.editorpane.editorbuffer.get_modified():
			# we need to prompt for save
			message = "Do you want to save the changes you have made?"
			dialog = gtk.MessageDialog(self.mainwindow,
							gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
							gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO,
							message)
			dialog.set_title("Save?")
			if dialog.run() == gtk.RESPONSE_NO: ret = False
			else: ret = True
			dialog.destroy()
		return ret

	def load_file(self, filename):
		while gtk.events_pending(): gtk.main_iteration()
		try:
			decode = self.editorpane.decode_text(filename)
			self.editorpane.fill_buffer(decode)
			self.filename = filename
			self.motion.create_environment(self.filename)
			self.motion.set_status("Loading file " + self.filename)
			self.add_recentfile(filename)
			self.set_window_title(self.filename)
		except:
			print traceback.print_exc()

	def write_file(self, filename):
		try:
			content = self.editorpane.grab_buffer()
			if filename: fout = open(filename, "w")
			else: fout = open(self.filename, "w")
			encoded = self.editorpane.encode_text(content)
			fout.write(encoded)
			fout.close()
			if filename: self.filename = filename
			self.motion.set_status("Saving file " + self.filename)
			self.motion.export_pdffile()
			self.set_window_title(self.filename)
		except:
			print traceback.print_exc()


	def gtk_main_quit(self, menuitem, data=None):
		if self.check_for_save(): self.on_menu_save_activate(None, None)
		if self.exitinterrupt is False:
			print "   ___ "
			print "  {o,o}	  Thanks for using Gummi!"
			print "  |)__)	  I welcome your feedback at:"
			print '  -"-"-	  http://gummi.midnightcoding.org\n'
			quit()
		else: self.exitinterrupt = False; return True


