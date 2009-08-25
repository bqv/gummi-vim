
# --------------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <alexvandermey@gmail.com> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return -Alexander van der Mey
# --------------------------------------------------------------------------------

import os
import sys
import gtk
import gobject
#import gtkunixprint
#import gconf

import texpane
import pdfpane
import motion
import prefs

if __name__ == '__main__':
	path = sys.argv[0]
else:
	path = __file__

INSTALLDIR = os.path.abspath(os.path.dirname(path))


class gummigui:

	def on_window_destroy(self, widget, data=None):
		gtk.main_quit()

	def __init__(self):

		self.filename = None
		self.installdir = INSTALLDIR

		builder = gtk.Builder()	
		builder.add_from_file(INSTALLDIR + "/gui/gummi.xml")
		builder.connect_signals(self)	

		self.mainwindow = builder.get_object("mainwindow")
		self.pdfdrawarea = builder.get_object("pdf_drawarea")
		self.editorport = builder.get_object("editor_viewport")
		self.menu1 = builder.get_object("menu1")
		self.statusbar = builder.get_object("statusbar")
		self.statusbar_cid = self.statusbar.get_context_id("Gummi")

		self.editorpane = texpane.texpane()
		self.editorport.add(self.editorpane.editorview)
		self.previewpane = pdfpane.pdfpane()
		self.motion = motion.motion(self)
		self.prefs = prefs.prefs(self)

		self.initial_document()	
		self.mainwindow.show_all()


	def initial_document(self):
		self.editorpane.bufferS.set_text(self.prefs.get_config_value("string", "default-text"))
		self.filename = '/tmp/gummi-default'	
		self.motion.create_environment(self.filename)
		self.motion.initial_preview()
		self.update_statusbar("")
		

	def update_statusbar(self, message):
		self.statusbar.push(self.statusbar_cid, message)


	def on_button_print_clicked(self, button, data=None):
		print "need to fix this"		
		#printDialog = gtkunixprint.PrintUnixDialog('Printer Settings',
		#						gtk.Window())      
		#printDialog.show_all()


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

	def on_menu_new_activate(self, menuitem, data=None):
		if self.check_for_save(): self.on_menu_save_activate(None, None)
		self.editorpane.bufferS.set_text("\documentclass{article}\n" +
						 "\\begin{document}\n.\n" +
						"\end{document}\n")
		self.editorpane.bufferS.set_modified(False)
		self.motion.create_environment("/tmp/gummi-new")
		self.motion.initial_preview()
		
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
			activeusr = os.getenv('USERNAME')
			os.chdir('/home/' + activeusr)
		filename = self.get_save_filename()
		if filename: self.write_file(filename)

	def on_menu_quit_activate(self, menuitem, data=None):
		if self.check_for_save(): self.on_menu_save_activate(None, None)
		print "Thanks for using Gummi! I welcome your feedback at \nhttp://code.google.com/p/gummi/"
		quit()

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

	def on_menu_about_activate(self, menuitem, data=None):
		authors = ["Alexander van der Mey"]
		about_dialog = gtk.AboutDialog()
		about_dialog.set_transient_for(self.mainwindow)
		about_dialog.set_destroy_with_parent(True)
		about_dialog.set_name("Gummi")
		about_dialog.set_version("0.1b")
		about_dialog.set_copyright("Copyright \xc2\xa9 2009 Alexander van der Mey")
		about_dialog.set_website("http://code.google.com/p/gummi/")
		about_dialog.set_comments("Simple LaTex Editor for GTK users")
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
	
	def gtk_main_quit(self, menuitem, data=None):
		#if self.check_for_save(): self.on_menu_save_activate(None, None)
		print "Thanks for using Gummi! I welcome your feedback at \nhttp://code.google.com/p/gummi/"
		quit()


	def get_open_filename(self):
		filename = None
		chooser = gtk.FileChooserDialog("Open File...", self.mainwindow,
										gtk.FILE_CHOOSER_ACTION_OPEN,
										(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
										gtk.STOCK_OPEN, gtk.RESPONSE_OK))
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
		#todo: add a file filter
		response = chooser.run()
		if response == gtk.RESPONSE_OK: filename = chooser.get_filename()
		chooser.destroy()
		return filename

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
			fin.close()

			self.editorpane.editorview.set_sensitive(False)
			buff = self.editorpane.editorview.get_buffer()
			buff.set_text(text)
			buff.set_modified(False)
			self.editorpane.editorview.set_sensitive(True)
			self.filename = filename
			self.motion.create_environment(self.filename)
			self.motion.initial_preview()
			self.update_statusbar("File: " + self.motion.texfile)
			#self.add_to_recentfiles(filename)
		except:
			self.error_message ("Could not open file: %s" % filename)

	def write_file(self, filename):
		try:
			buff = self.editorpane.editorview.get_buffer()
			self.editorpane.editorview.set_sensitive(False)
			text = buff.get_text(buff.get_start_iter(), buff.get_end_iter())
			self.editorpane.editorview.set_sensitive(True)
			buff.set_modified(False)
			
			if filename: fout = open(filename, "w")
			else: fout = open(self.filename, "w")
			fout.write(text)
			fout.close()

			if filename: self.filename = filename        
		except:
			self.error_message ("Could not save file: %s" % filename)

if __name__ == "__main__":
	editor = gummigui()
	editor.mainwindow.show()
	gtk.main()

