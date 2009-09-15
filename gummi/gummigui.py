
# --------------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <alexvandermey@gmail.com> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return -Alexander van der Mey
# --------------------------------------------------------------------------------

import os
import sys
import gtk
import pango
import gobject
import codecs
import traceback
import gtksourceview2

import texpane
import pdfpane
import updatecheck
import motion
import prefs

if __name__ == '__main__':
	path = sys.argv[0]
else:
	path = __file__

INSTALLDIR = os.path.abspath(os.path.dirname(path))
VERSION = "svn"


class gummigui:

	def on_window_destroy(self, widget, data=None):
		gtk.main_quit()

	def __init__(self):

		if len(sys.argv) > 1: 
			self.filename = sys.argv[1]
		else: self.filename = None
		self.installdir = INSTALLDIR
		self.version = VERSION

		self.start_iter = None
		self.current_iter = None
		self.searchflags = 0

		builder = gtk.Builder()	
		builder.add_from_file(INSTALLDIR + "/gui/gummi.xml")
		builder.connect_signals(self)	

		self.mainwindow = builder.get_object("mainwindow")
		self.pdfdrawarea = builder.get_object("pdf_drawarea")
		self.menu1 = builder.get_object("menu1")
		self.statusbar = builder.get_object("statusbar")
		self.searchwindow = builder.get_object("searchwindow")
		self.searchentry = builder.get_object("searchentry")
		self.statusbar_cid = self.statusbar.get_context_id("Gummi")
		self.editorscroll = builder.get_object("editor_scroller")
		self.backwards = builder.get_object("toggle_backwards")	
		self.errorviewer = builder.get_object("errorfield")
		self.statuslight = builder.get_object("statuslight")

		self.editorpane = texpane.texpane()
		self.editorscroll.add(self.editorpane.editorview)
		self.previewpane = pdfpane.pdfpane()
		self.motion = motion.motion(self)
		self.prefs = prefs.prefs(self)

		self.buffer = self.editorpane.bufferS
		self.errorviewer.modify_font(pango.FontDescription("monospace 8"))
		self.errorbuffer = self.errorviewer.get_buffer()		
		self.initial_document()	
		self.mainwindow.show_all()


	def initial_document(self):
		if self.filename is None:
			self.editorpane.bufferS.set_text(self.prefs.get_config_value("string", "tex_defaulttext"))
			self.filename = '/tmp/gummi-default'	
			self.editorpane.bufferS.set_modified(False)
			self.motion.create_environment(self.filename)		
		else:
			self.load_file(self.filename)	
		self.editorpane.bufferS.set_modified(False)
		self.update_statusbar("")
		

	def update_statusbar(self, message):
		self.statusbar.push(self.statusbar_cid, message)


	def on_button_print_clicked(self, button, data=None):
		print "need to fix this"		
		#printDialog = gtkunixprint.PrintUnixDialog('Printer Settings',
		#						gtk.Window())      
		#printDialog.show_all()


	def on_bold_button_clicked(self, widget, data=None):
		self.editorpane.set_selection_bold(widget)

	def on_italic_button_clicked(self, widget, data=None):
		self.editorpane.set_selection_italic(widget)

	def on_unline_button_clicked(self, widget, data=None):
		self.editorpane.set_selection_unline(widget)


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

	def on_button_searchwindow_close_clicked(self, button, data=None):
		self.searchwindow.hide()
		return True

	def on_button_searchwindow_find_clicked(self, button, data=None):
		term = self.searchentry.get_text()
		if self.backwards.get_active() is False: 
			try:
				ins, bound = gtksourceview2.iter_forward_search(self.current_iter, term, self.searchflags, limit=None)
				self.current_iter = bound			
			except:			
				return	
		else:	
			try:
				ins, bound = gtksourceview2.iter_backward_search(self.current_iter, term, self.searchflags, limit=None)
				self.current_iter = ins			
			except:
				return
		self.buffer.place_cursor(ins)
		self.buffer.select_range(ins, bound)
		self.editorpane.editorview.scroll_to_iter(ins, 0)


	# maybe integrate it into the search function.. 
	def toggle_searchwindow_matchcase(self, widget, data=None):
		if widget.get_active() is True:
			self.searchflags = 0
		else:
			self.searchflags = (gtksourceview2.SEARCH_CASE_INSENSITIVE)

	#def toggle_searchwindow_wholeword(self):

	def on_menu_find_activate(self, menuitem, data=None):
		self.start_iter = self.buffer.get_start_iter()
		self.current_iter = self.buffer.get_iter_at_mark(self.buffer.get_insert())		
		self.searchentry.grab_focus()
		self.searchentry.set_text("")
		self.searchwindow.show()
		

	def on_searchwindow_delete_event(self, widget, data=None):
		self.searchwindow.hide()
		return True


	def on_menu_new_activate(self, menuitem, data=None):
		if self.check_for_save(): self.on_menu_save_activate(None, None)
		self.editorpane.bufferS.set_text("\documentclass{article}\n" +
						 "\\begin{document}\n.\n" +
						"\end{document}\n")
		self.editorpane.bufferS.set_modified(False)
		self.motion.create_environment("/tmp/gummi-new")
		self.filename = None
		
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
		if self.editorpane.editorview.get_buffer().can_undo():
			self.editorpane.editorview.get_buffer().undo()

	def on_menu_redo_activate(self, menuitem, data=None):
		if self.editorpane.editorview.get_buffer().can_redo():
			self.editorpane.editorview.get_buffer().redo()

	def on_menu_cut_activate(self, menuitem, data=None):
		buff = self.editorpane.editorview.get_buffer();
		buff.cut_clipboard (gtk.clipboard_get(), True);

	def on_menu_copy_activate(self, menuitem, data=None):
		buff = self.editorpane.editorview.get_buffer();
		buff.copy_clipboard (gtk.clipboard_get());

	def on_menu_paste_activate(self, menuitem, data=None):
		buff = self.editorpane.editorview.get_buffer();
		buff.paste_clipboard (gtk.clipboard_get(), None, True);

	def on_menu_delete_activate(self, menuitem, data=None):
		buff = self.editorpane.editorview.get_buffer();
		buff.delete_selection (False, True);

	def on_menu_selectall_activate(self, menuitem, data=None):
		buff = self.editorpane.editorview.get_buffer();
		buff.select_range(buff.get_start_iter(),buff.get_end_iter())


	def on_menu_preferences_activate(self, menuitem, data=None):
		self.prefs.create_gui()

	def on_menu_update_activate(self, menuitem, data=None):
		self.updater = updatecheck.updatecheck(self)

	def on_menu_about_activate(self, menuitem, data=None):
		
		authors = ["Alexander van der Mey\n<alexvandermey@gmail.com>"]
		about_dialog = gtk.AboutDialog()
		about_dialog.set_transient_for(self.mainwindow)
		about_dialog.set_destroy_with_parent(True)
		about_dialog.set_name("Gummi")
		about_dialog.set_version(VERSION)
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
			self.motion.create_environment(filename)		
			chooser.destroy()
		return filename


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


	def check_for_save(self):
		ret = False
		if self.editorpane.bufferS.get_modified():
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
			
			fin = open(filename, "r")
			text = fin.read()
			decodedtxt = text.decode("iso-8859-1")
			fin.close()

			self.editorpane.editorview.set_sensitive(False)
			buff = self.editorpane.editorview.get_buffer()
			buff.set_text(decodedtxt)
			buff.set_modified(False)
			self.editorpane.editorview.set_sensitive(True)
			self.filename = filename
			self.motion.create_environment(self.filename)
			self.update_statusbar("Loaded: " + self.motion.texfile)
			#self.add_to_recentfiles(filename)
		except:
			print traceback.print_exc()


	def write_file(self, filename):
		try:
			buff = self.editorpane.editorview.get_buffer()
			self.editorpane.editorview.set_sensitive(False)
			text = buff.get_text(buff.get_start_iter(), buff.get_end_iter())
			self.editorpane.editorview.set_sensitive(True)
			buff.set_modified(False)
			
			if filename: fout = open(filename, "w")
			else: fout = open(self.filename, "w")

			encodedtxt = text.encode("iso-8859-1")
			fout.write(encodedtxt)
			fout.close()

			if filename: self.filename = filename        
			self.update_statusbar("Saved: " + self.motion.texfile)		
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
	editor = gummigui()
	editor.mainwindow.show()
	gtk.main()

