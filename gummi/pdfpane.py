
# --------------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <alexvandermey@gmail.com> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return -Alexander van der Mey
# --------------------------------------------------------------------------------

import gtk
import poppler


class pdfpane:
	
	def __init__(self):

		self.pdffile = None
		self.drawarea = None
		self.page_displayed = 0
		self.page_total = None
		
		self.scale = 1
		self.maxscale = 1.6 
		self.minscale = 1.0	
		self.scale_rate = 0.1

	def create_previewpane(self, pdffile, drawarea):
		self.pdffile = pdffile
		self.drawarea = drawarea	
		self.uri = "file://" + pdffile
		self.document = poppler.document_new_from_file(self.uri, None)
		self.page_total = self.document.get_n_pages()
		self.current_page = self.document.get_page(self.page_displayed)
		self.width, self.height = self.current_page.get_size()
		self.drawarea.set_size_request(int(self.width), int(self.height))
		self.drawarea.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(6400, 6400, 6440))
		self.drawarea.connect("expose-event", self.on_expose)

	def refresh_previewpane(self):
		self.uri = "file://" + self.pdffile
		self.document = poppler.document_new_from_file(self.uri, None)
		self.page_total = self.document.get_n_pages()
		self.current_page = self.document.get_page(self.page_displayed)
		self.drawarea.queue_draw() 

	def jump_to_nextpage(self):
		if (self.page_displayed + 1) < self.page_total:
			self.page_displayed = self.page_displayed + 1
			self.uri = "file://" + self.pdffile
			self.document = poppler.document_new_from_file(self.uri, None)
			self.page_total = self.document.get_n_pages()
			self.current_page = self.document.get_page(self.page_displayed)
			self.drawarea.queue_draw()
		
	def jump_to_prevpage(self):
		if (self.page_displayed - 1) >= 0:
			self.page_displayed = self.page_displayed - 1
			self.uri = "file://" + self.pdffile
			self.document = poppler.document_new_from_file(self.uri, None)
			self.page_total = self.document.get_n_pages()
			self.current_page = self.document.get_page(self.page_displayed)
			self.drawarea.queue_draw()

	def zoom_in_pane(self):
		if self.scale < self.maxscale:
			self.scale = self.scale + 0.1
			self.width = (self.width * 1.1)
			self.height = (self.height * 1.1)
			self.drawarea.set_size_request(int(self.width), int(self.height))
			self.refresh_previewpane()

	def zoom_out_pane(self):
		if self.scale > self.minscale:
			self.scale = self.scale - 0.1
			self.width = (self.width / 1.1) 
			self.height = (self.height / 1.1) 
			self.drawarea.set_size_request(int(self.width), int(self.height))
			self.refresh_previewpane()

	def zoom_normal_pane(self):
		# method needs rewrite
		self.scale = 1
		self.height = 841.89 
		self.width = 595.276 
		self.drawarea.set_size_request(int(self.height), int(self.width))
		self.refresh_previewpane()

	def on_expose(self, widget, event):
		cr = widget.window.cairo_create()
		cr.set_source_rgb(1, 1, 1)
		cr.translate(0, 0)
		if self.scale != 1:
			cr.scale(self.scale, self.scale)
		cr.rectangle(0, 0, self.width, self.height)
		cr.fill()
		self.current_page.render(cr)


