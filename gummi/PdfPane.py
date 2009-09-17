
# --------------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <alexvandermey@gmail.com> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return -Alexander van der Mey
# --------------------------------------------------------------------------------

import gtk
import poppler

ORIGINAL_HEIGHT = 841.89 
ORIGINAL_WIDTH  = 595.276 


class PdfPane:

	def __init__(self, drawarea):
		self.drawarea = drawarea
		self.scale = 1
		self.maxscale = 1.6 
		self.minscale = 1.0
		self.page_displayed = 0
		self.page_total = None

	def create_preview(self, pdffile):
		self.pdffile = pdffile	
		self.uri = "file://" + pdffile
		self.document = poppler.document_new_from_file(self.uri, None)
		self.page_total = self.document.get_n_pages()
		self.current_page = self.document.get_page(0)
		self.width, self.height = self.current_page.get_size()
		self.drawarea.set_size_request(int(self.width), int(self.height))
		self.drawarea.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(6400, 6400, 6440))
		self.drawarea.connect("expose-event", self.on_expose)

	def refresh_preview(self):
		self.drawarea.show()
		self.uri = "file://" + self.pdffile
		self.document = poppler.document_new_from_file(self.uri, None)
		self.page_total = self.document.get_n_pages()
		if self.page_total <= (self.page_displayed):		
			self.current_page = self.document.get_page(self.page_total - 1)			
		else:		
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
			self.refresh_preview()

	def zoom_out_pane(self):
		if self.scale > self.minscale:
			self.scale = self.scale - 0.1
			self.width = (self.width / 1.1) 
			self.height = (self.height / 1.1) 
			self.drawarea.set_size_request(int(self.width), int(self.height))
			self.refresh_preview()

	def zoom_normal_pane(self):
		self.scale = 1
		self.height = ORIGINAL_HEIGHT
		self.width = ORIGINAL_WIDTH
		self.drawarea.set_size_request(int(self.width), int(self.height))
		self.refresh_preview()

	def on_expose(self, widget, event):
		cr = widget.window.cairo_create()
		cr.set_source_rgb(1, 1, 1)
		cr.translate(0, 0)
		if self.scale != 1:
			cr.scale(self.scale, self.scale)
		cr.rectangle(0, 0, self.width, self.height)
		cr.fill()
		self.current_page.render(cr)



