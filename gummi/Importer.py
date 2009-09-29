
# --------------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <alexvandermey@gmail.com> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return -Alexander van der Mey
# --------------------------------------------------------------------------------

import gtk


class Importer: # needs cleanup

	def __init__(self, editorpane, builder):
		self.editorpane = editorpane

		self.mainwindow = builder.get_object("mainwindow")

		self.import_tabs = builder.get_object("import_tabs")
		self.image_pane = builder.get_object("image_pane")
		self.image_file = builder.get_object("image_file")
		self.image_caption = builder.get_object("image_caption")
		self.image_label = builder.get_object("image_label")
		self.image_scale = builder.get_object("image_scale")
		self.scaler = builder.get_object("scaler")
		self.table_pane = builder.get_object("table_pane")
		self.table_rows = builder.get_object("table_rows")
		self.table_cols = builder.get_object("table_cols")

		self.table_cols.set_value(3)
		self.table_rows.set_value(3)

		self.bcenter = "\n\\begin{center}\n"
		self.ecenter = "\\end{center}\n"



	def prepare_image(self):
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

	def insert_image(self):
		if self.image_file.get_text() is not "":	
			self.editorpane.insert_package("graphicx")		
			f = self.image_file.get_text()			
			s = self.scaler.get_value()
			c = self.image_caption.get_text()
			l = self.image_label.get_text()
			code = self.generate_image(f, s, c, l)	
			iter = self.editorpane.get_current_position()			
			self.editorpane.editorbuffer.insert(iter, code)
			self.editorpane.text_changed()
		self.import_tabs.set_current_page(0)

	def insert_table(self):
		iter = self.editorpane.get_current_position()				
		code = self.generate_table(self.table_rows.get_value(), self.table_cols.get_value())	
		iter = self.editorpane.get_current_position()			
		self.editorpane.editorbuffer.insert(iter, code)
		self.editorpane.text_changed()
		self.import_tabs.set_current_page(0)

	def generate_table(self, rows, columns):
		allign = ""
		table = ""
		rows = int(rows) + 1
		columns = int(columns) + 1
		for l in range(1,columns): allign = allign + "l"
		begin_tabular = 	"\\begin{tabular}{" + allign + "}\n"
		end_tabular = "\\end{tabular}\n"
		for k in range(1, rows):		
			for i in range(1,columns):
				if i == (columns-1): new = str(k) + str(i) + "\\\\ \n"
				elif i == 1: new = "\t" + str(k) + str(i) + " & " 
				else: new = str(k) + str(i) + " & " 
				table = table + new
		return begin_tabular + table + end_tabular


	def generate_image(self, imagefile,  scale, caption, label):
		include = "\t\\includegraphics"
		scale = "[scale=" + str(scale) + "]"
		file = "{" + imagefile + "}\n"
		caption = "\t\\captionof{" + caption + "}\n"
		label = "\t\\label{" + label + "}\n"
		end = "\\end{center}\n"
		return self.bcenter + include + scale + file + caption + label + end













