
# --------------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <alexvandermey@gmail.com> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return -Alexander van der Mey
# --------------------------------------------------------------------------------

import os
import sys
import gtk
import locale
import gtksourceview2
import traceback
import pango
try: import glib
except: pass

import TexPane
import PdfPane
import Motion
import Preferences
import UpdateCheck


class GummiGUI:

	def __init__(self):

		self.filename = None
		self.CWD = CWD

		builder = gtk.Builder()
		builder.add_from_file(CWD + "/gui/gummi.xml")
		builder.connect_signals(self)

		self.mainwindow = builder.get_object("mainwindow")
		self.editorscroll = builder.get_object("editor_scroll")
		self.drawarea = builder.get_object("preview_drawarea")
		self.errorfield = builder.get_object("errorfield")
		self.searchwindow = builder.get_object("searchwindow")
		self.searchentry = builder.get_object("searchentry")
		self.backwards = builder.get_object("toggle_backwards")	
		self.matchcase = builder.get_object("toggle_matchcase")
		self.statuslight = builder.get_object("tool_statuslight")
		self.statusbar = builder.get_object("statusbar")
		self.statusbar_cid = self.statusbar.get_context_id("Gummi")
		self.errorfield.modify_font(pango.FontDescription("monospace 8"))
		self.recent1 = builder.get_object("menu_recent1")		
		self.recent2 = builder.get_object("menu_recent2")
		self.recent3 = builder.get_object("menu_recent3")

		self.image_pane = builder.get_object("image_pane")
		self.image_file = builder.get_object("image_file")
		self.image_caption = builder.get_object("image_caption")
		self.image_label = builder.get_object("image_label")
		self.image_scale = builder.get_object("image_scale")
		self.scaler = builder.get_object("scaler")

		self.config = Preferences.Preferences(self)
		self.editorpane = TexPane.TexPane(self.config)
		self.previewpane = PdfPane.PdfPane(self.drawarea)
		self.motion = Motion.Motion(self.editorpane, self.previewpane, self.errorfield, self.statuslight)
		self.editorscroll.add(self.editorpane.editorviewer)

		self.create_initial_document()
		self.mainwindow.show_all()
	
	def create_initial_document(self):
		if len(sys.argv) > 1: 
			self.filename = sys.argv[1]		
			self.load_file(self.filename)
		else: 
			self.filename = "/tmp/gummi-default"
			self.editorpane.fill_buffer(self.config.get_string("tex_defaulttext"))
			self.motion.create_environment(self.filename)
			os.chdir(os.environ['HOME'])
		self.setup_recentfiles()

	def decode_text(self, filename):
		loadfile = open(filename, "r")
		content = loadfile.read()
		lang, encoding = locale.getdefaultlocale()
		try: decoded_content = content.decode(encoding)
		except (UnicodeError, TypeError):
			try: decoded_content = content.decode("iso-8859-1", 'replace')
			except (UnicodeError, TypeError):
				decoded_content = content.decode("ascii", 'replace')
		loadfile.close()
		return decoded_content

	def encode_text(self, text):
		lang, encoding = locale.getdefaultlocale()
		try: encoded_content = text.encode(encoding)
		except (UnicodeError, TypeError):
			try: encoded_content = text.encode("iso-8859-1", 'replace')
			except (UnicodeError, TypeError):
				encoded_content = content.encode("ascii", 'replace')
		return encoded_content

	def update_statusbar(self, message):
		self.statusbar.push(self.statusbar_cid, message)

	def on_menu_new_activate(self, menuitem, data=None):
		if self.check_for_save(): self.on_menu_save_activate(None, None)
		self.editorpane.fill_buffer(Preferences.DEFAULT_TEXT)
		self.editorpane.editorbuffer.set_modified(False)
		self.filename = None
		self.motion.create_environment("/tmp/gummi-new")

	def on_menu_open_activate(self, menuitem, data=None):
		if os.getcwd() == '/tmp':
			os.chdir(os.environ['HOME'])	
		if self.check_for_save(): self.on_menu_save_activate(None, None)        
		filename = self.get_open_filename()
		if filename: self.load_file(filename)

	def on_menu_save_activate(self, menuitem, data=None):
		if os.getcwd() == '/tmp':
			os.chdir(os.environ['HOME'])	
		if self.filename is None: 
			filename = self.get_save_filename()
			if filename: self.write_file(filename)
		if os.path.dirname(self.filename) == "/tmp":
			filename = self.get_save_filename()
			if filename: self.write_file(filename)
		else: self.write_file(None)

	def on_menu_saveas_activate(self, menuitem, data=None):	
		if os.getcwd() == '/tmp':
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
		self.editorpane.trigger_update()

	def on_menu_copy_activate(self, menuitem, data=None):
		buff = self.editorpane.editorviewer.get_buffer()
		buff.copy_clipboard (gtk.clipboard_get())

	def on_menu_paste_activate(self, menuitem, data=None):
		buff = self.editorpane.editorviewer.get_buffer()
		buff.paste_clipboard (gtk.clipboard_get(), None, True)
		self.editorpane.trigger_update()

	def on_menu_delete_activate(self, menuitem, data=None):
		buff = self.editorpane.editorviewer.get_buffer()
		buff.delete_selection (False, True)

	def on_menu_selectall_activate(self, menuitem, data=None):
		buff = self.editorpane.editorviewer.get_buffer()
		buff.select_range(buff.get_start_iter(),buff.get_end_iter())

	def on_menu_find_activate(self, menuitem, data=None):
		self.editorpane.start_searchfunction()	
		self.searchentry.grab_focus()
		self.searchentry.set_text("")
		self.searchwindow.show()

	def on_button_searchwindow_close_clicked(self, button, data=None):
		self.searchwindow.hide()
		return True

	def on_button_searchwindow_find_clicked(self, button, data=None):
		term = self.searchentry.get_text()
		flags = self.get_search_flags()
		self.editorpane.search_buffer(term, flags)

	def on_import_tabs_switch_page(self, notebook, page, page_num):
		newactive = notebook.get_nth_page(page_num).get_name()
		if newactive == "box_image": self.image_pane.show()
		if newactive == "box_minimize": self.image_pane.hide()
		if newactive == "box_table": self.image_pane.hide()

	def on_image_file_activate(self, button, event, data=None):
		imagefile = None
		chooser = gtk.FileChooserDialog("Open File...", self.mainwindow,
								gtk.FILE_CHOOSER_ACTION_OPEN,
								(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
								gtk.STOCK_OPEN, gtk.RESPONSE_OK))
		imagefilter = gtk.FileFilter()
		imagefilter.set_name('Image files')
		imagefilter.add_mime_type("image/*")
		chooser.add_filter(imagefilter)

		response = chooser.run()
		if response == gtk.RESPONSE_OK: imagefile = chooser.get_filename()
		chooser.destroy()
		self.image_label.set_sensitive(True)
		self.image_scale.set_sensitive(True)
		self.image_caption.set_sensitive(True)
		self.scaler.set_value(1.00)
		self.image_file.set_text(imagefile)
		return imagefile

	def prepare_image_import(self, imagefile):
		begin = "\n\\begin{center}\n"
		include = "\t\\includegraphics"
		scale = "[scale=" + str(self.scaler.get_value()) + "]"
		file = "{" + self.image_file.get_text() + "}\n"
		caption = "\t\\captionof{" + self.image_caption.get_text() + "}\n"
		label = "\t\\label{" + self.image_label.get_text() + "}\n"
		end = "\\end{center}\n"
		return begin + include + scale + file + caption + label + end

	def on_button_imagewindow_apply_clicked(self, button, data=None):
		if self.image_file.get_text() is not "":
			iter = self.editorpane.get_current_position()		
			self.editorpane.insert_package("graphicx", iter)		
			code = self.prepare_image_import("")		
			iter = self.editorpane.get_current_position()			
			self.editorpane.editorbuffer.insert(iter, code)
			self.editorpane.text_changed()
		self.image_pane.hide()			

	def get_search_flags(self):
		flags = [False, 0]
		if self.backwards.get_active() is True: flags[0] = True
		else: flags[0] = False
		if self.matchcase.get_active() is True: flags[1] = 0
		else: flags[1] = (gtksourceview2.SEARCH_CASE_INSENSITIVE)
		return flags

	def on_menu_image_activate(self, menuitem, data=None):
		self.importpane.show()

	def on_menu_preferences_activate(self, menuitem, data=None):
		self.config.display_preferences()

	def on_menu_update_activate(self, menuitem, data=None):
		checkforupdates = UpdateCheck.UpdateCheck()

	def on_menu_about_activate(self, menuitem, data=None):		
		authors = ["Alexander van der Mey\n<alexvandermey@gmail.com>"]
		about_dialog = gtk.AboutDialog()
		about_dialog.set_transient_for(self.mainwindow)
		about_dialog.set_destroy_with_parent(True)
		about_dialog.set_name("Gummi")
		about_dialog.set_version(Preferences.VERSION)
		about_dialog.set_copyright("Copyright \xc2\xa9 2009 Alexander van der Mey")
		about_dialog.set_website("http://gummi.googlecode.com")
		about_dialog.set_comments("Simple LaTex Editor for GTK+ users")
		about_dialog.set_authors            (authors)
		about_dialog.set_logo_icon_name     (gtk.STOCK_EDIT)
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

	def on_tool_italic_activate(self, button, data=None):
		self.editorpane.set_selection_textstyle(button)

	def on_tool_unline_activate(self, button, data=None):
		self.editorpane.set_selection_textstyle(button)

	def on_button_pageback_clicked(self, button, data=None):
		self.previewpane.jump_to_prevpage()

	def on_button_pageforward_clicked(self, button, data=None):
		self.previewpane.jump_to_nextpage()

	def on_button_zoomin_clicked(self, button, data=None):
		self.previewpane.zoom_in_pane()

	def on_button_zoomout_clicked(self, button, data=None):
		self.previewpane.zoom_out_pane()
	
	def on_button_zoomnormal_clicked(self, button, data=None):
		self.previewpane.zoom_normal_pane()

	def set_status(self, message):
		self.statusbar.push(self.statusbar_cid, message)
		glib.timeout_add(4000, self.remove_status)

	def remove_status(self):
		self.statusbar.push(self.statusbar_cid, "")

	def setup_recentfiles(self):
		self.check_recentfile(0, self.recent1)
		self.check_recentfile(1, self.recent2)
		self.check_recentfile(2, self.recent3)

	def check_recentfile(self, i, widget):
		recents = self.config.get_list("recent_files")
		try:
			recents[i]
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
		if response == gtk.RESPONSE_OK: 
			filename = chooser.get_filename()
			if not ".tex" in filename[-4:]:
				filename = filename + ".tex"		
			chooser.destroy()
			self.motion.create_environment(filename)	
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
			decode = self.decode_text(filename)
			self.editorpane.fill_buffer(decode)
			self.filename = filename
			self.motion.create_environment(self.filename)
			self.set_status("Loading: " + self.filename)
			self.add_recentfile(filename)
		except:
			print traceback.print_exc()

	def write_file(self, filename):
		try:
			content = self.editorpane.grab_buffer()			
			if filename: fout = open(filename, "w")
			else: fout = open(self.filename, "w")
			encoded = self.encode_text(content)
			fout.write(encoded)
			fout.close()
			if filename: self.filename = filename   
			self.set_status("Saving: " + self.filename)
			self.motion.export_pdffile()	
		except:
			print traceback.print_exc()


	def gtk_main_quit(self, menuitem, data=None):
		if self.check_for_save(): self.on_menu_save_activate(None, None)	
		print "   ___ "
		print "  {o,o}	  Thanks for using Gummi!"
		print "  |)__)	  I welcome your feedback at:"
		print '  -"-"-	  http://gummi.googlecode.com\n'
		quit()


if __name__ == "__main__":
	path = sys.argv[0]
else:
	path = __file__
CWD = os.path.abspath(os.path.dirname(path))
try: 
	instance = GummiGUI()
	instance.mainwindow.show()
	gtk.main()
except:
	print traceback.print_exc()
