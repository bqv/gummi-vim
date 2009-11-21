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

import Importer
import UpdateCheck
import Template
import Preferences


class MainGUI:

	def __init__(self, parent, config, iofunc):
		self.core = parent
		self.config = config
		self.editorpane = self.core.editorpane
		self.previewpane = self.core.previewpane
		self.biblio = self.core.biblio
		self.iofunc = iofunc

		self.path = self.core.path
		self.tempdir = self.core.tempdir
		self.builder = self.core.builder
		self.exitinterrupt = False
		
		self.mainwindow = self.builder.get_object("mainwindow")
		self.toolbar = self.builder.get_object("toolbar")
		self.mainnotebook = self.builder.get_object("main_notebook")
		self.editorscroll = self.builder.get_object("editor_scroll")
		self.drawarea = self.builder.get_object("preview_drawarea")
		self.preview_toolbar = self.builder.get_object("preview_toolbar")
		
		self.hpaned = self.builder.get_object("hpaned")
		mainwidth = self.mainwindow.get_size()[0]
		self.hpaned.set_position(mainwidth/2)

		self.editorscroll.add(self.editorpane.editorviewer)
		self.importgui = ImportGUI(self.builder, self.editorpane)
		self.recentgui = RecentGUI(self.builder, self.config, self)
		self.searchgui = SearchGUI(self.builder, self.editorpane)
	
		self.builder.connect_signals(self) #split signals?


	def main(self):
		self.mainwindow.show_all()
		gtk.main()

	def set_window_title(self, filename):
		self.mainwindow.set_title \
					(os.path.basename(filename) + " - Gummi")

	def on_menu_new_activate(self, menuitem, data=None):
		if self.check_for_save(): self.on_menu_save_activate(None, None)
		self.editorpane.fill_buffer(self.config.get_string("tex_defaulttext"))
		self.editorpane.editorbuffer.set_modified(False)
		self.filename = None
		self.iofunc.make_environment(self.filename)

	def on_menu_template_activate(self, menuitem, data=None):
		self.template_doc = Template.Template(self.builder, self.path)

	def on_menu_open_activate(self, menuitem, data=None):
		if os.getcwd() == self.tempdir:
			os.chdir(os.environ['HOME'])
		if self.check_for_save(): self.on_menu_save_activate(None, None)
		filename = self.get_open_filename()
		if filename: self.load_document(filename)

	def on_menu_save_activate(self, menuitem, data=None):
		if os.getcwd() == self.tempdir:
			os.chdir(os.environ['HOME'])
		if self.iofunc.filename is None:
			filename = self.get_save_filename()
			if filename: self.save_document(filename)
		if os.path.dirname(self.filename) == self.tempdir:
			filename = self.get_save_filename()
			if filename: self.save_document(filename)
		else: self.save_document(None)

	def on_menu_saveas_activate(self, menuitem, data=None):
		if os.getcwd() == self.tempdir:
			os.chdir(os.environ['HOME'])
		self.filename = self.get_save_filename()
		if self.filename: self.save_document(self.filename)

	def on_menu_recent_activate(self, widget, data=None):
		self.recentgui.activate_recentfile(widget)

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
		self.searchgui.show_searchwindow()		

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

	def on_menu_statusbar_toggled(self, menuitem, data=None):
		if menuitem.get_active():
			self.iofunc.statusbar.show()
		else:
			self.iofunc.statusbar.hide()

	def on_button_searchwindow_close_clicked(self, button, data=None):
		self.searchgui.close_searchwindow()

	def on_button_searchwindow_find_clicked(self, button, data=None):
		self.searchgui.start_search()

	def on_import_tabs_switch_page(self, notebook, page, page_num):
		self.importgui.show_importpane(notebook, page_num)

	def on_button_template_ok_clicked(self, button, data=None):
		template = self.template_doc.get_template()
		if template is not None:
			self.editorpane.fill_buffer(template)
			self.filename = None
			self.iofunc.make_environment(self.tempdir + "/gummi-new")
			self.template_doc.templatewindow.hide()
		else: pass

	def on_button_template_cancel_clicked(self, button, data=None):
		self.template_doc.templatewindow.hide()
		return True

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

	def on_tool_textstyle_activate(self, button, data=None):
		self.editorpane.set_selection_textstyle(button)

	def on_button_import_apply_clicked(self, button, data=None):
		self.importgui.insert_object(button)

	def on_image_file_activate(self, button, event, data=None):
		self.importgui.choose_imagefile()

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
			self.iofunc.make_environment(filename)
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


	def load_document(self, filename):
		while gtk.events_pending(): gtk.main_iteration()
		try:
			self.iofunc.load_file(filename)
			self.filename = filename
			self.recentgui.add_recentfile(self.filename)
			self.set_window_title(self.filename)
		except:
			print traceback.print_exc()


	def save_document(self, filename):
		try:
			self.iofunc.save_file(filename)
			if filename: self.filename = filename
			self.iofunc.set_status("Saving file " + self.filename)
			self.iofunc.export_pdffile()
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






class SearchGUI:

	def __init__(self, builder, editorpane):
		self.builder = builder
		self.editorpane = editorpane
		self.setup_searchwindow()

	def setup_searchwindow(self):
		self.searchwindow = self.builder.get_object("searchwindow")
		self.searchentry = self.builder.get_object("searchentry")
		self.backwards = self.builder.get_object("toggle_backwards")
		self.matchcase = self.builder.get_object("toggle_matchcase")

	def show_searchwindow(self):
		self.searchentry.set_text("")
		self.searchwindow.show()

	def close_searchwindow(self):
		self.searchwindow.hide()
		return True

	def start_search(self):
		term = self.searchentry.get_text()
		backwards = self.backwards.get_active()
		matchcase = self.matchcase.get_active()
		self.editorpane.search_buffer(term, backwards, matchcase)





class ImportGUI:

	def __init__(self, builder, editorpane):
		self.builder = builder
		self.editorpane = editorpane
		self.setup_importpanes()

	def setup_importpanes(self):
		self.box_image = self.builder.get_object("box_image")
		self.box_table = self.builder.get_object("box_table")
		self.box_matrix = self.builder.get_object("box_matrix")
		self.image_pane = self.builder.get_object("image_pane")
		self.table_pane = self.builder.get_object("table_pane")
		self.matrix_pane = self.builder.get_object("matrix_pane")
		self.importer = Importer.Importer(self.editorpane, self.builder)

	def show_importpane(self, notebook, page_num):
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

	def insert_object(self, widget):
		caller = widget.get_name()
		if caller == "table_apply":
			self.importer.insert_table()
		elif caller == "image_apply":
			self.importer.insert_image()
		elif caller == "matrix_apply":
			self.importer.insert_matrix()

	def choose_imagefile(self):
		self.importer.prepare_image()	




class RecentGUI:

	def __init__(self, builder, config, parent):		
		self.builder = builder
		self.config = config
		self.parent = parent
		self.setup_recentfiles()

	def setup_recentfiles(self):
		self.recent1 = self.builder.get_object("menu_recent1")
		self.recent2 = self.builder.get_object("menu_recent2")
		self.recent3 = self.builder.get_object("menu_recent3")
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

	def activate_recentfile(self, widget):
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
		self.parent.check_for_save()
		self.parent.load_document(filename)

