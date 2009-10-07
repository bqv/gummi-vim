
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

import gtk
import poppler
import traceback
import os.path

ORIGINAL_HEIGHT = 841.89 
ORIGINAL_WIDTH  = 595.276


class PdfPane:

	def __init__(self, config, builder):
		self.config = config
		self.drawarea = builder.get_object("preview_drawarea")
		self.button_bestfit = builder.get_object("button_bestfit")

		self.scale = 1
		self.maxscale = 2.0 
		self.minscale = 1.0
		self.page_displayed = 0
		self.page_total = None
		self.previewactive = 0
		self.bestfit_active = True
		self.i = 0

		self.pdffile = None


	def create_preview(self, pdffile):
		self.pdffile = pdffile	
		self.uri = "file://" + pdffile
		self.document = poppler.document_new_from_file(self.uri, None)
		self.page_total = self.document.get_n_pages()
		self.current_page = self.document.get_page(0)
		self.width, self.height = self.current_page.get_size()
		self.drawarea.set_size_request(int(self.width), int(self.height))
		self.drawarea.modify_bg(gtk.STATE_NORMAL,
								gtk.gdk.Color(6400, 6400, 6440))
		self.drawarea.connect("expose-event", self.on_expose)
		self.previewactive = True

	def refresh_preview(self):
		if not self.previewactive: self.create_preview(self.pdffile)
		try:
			if os.path.exists(self.pdffile): # only refresh if file exists
				self.drawarea.show()
				self.uri = "file://" + self.pdffile
				self.document = poppler.document_new_from_file(self.uri, None)
				self.page_total = self.document.get_n_pages()
				if self.page_total <= (self.page_displayed):		
					self.current_page = self.document.get_page(self.page_total - 1)			
				else:		
					self.current_page = self.document.get_page(self.page_displayed)
				self.drawarea.queue_draw()
		except: print traceback.print_exc()

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
		self.autozoom = False
		if self.scale < self.maxscale:
			self.scale = self.scale + 0.1
			self.drawarea.set_size_request(int(self.width*self.scale), int(self.height*self.scale))
			self.refresh_preview()
		self.set_bestfitmode(False)

	def zoom_out_pane(self):
		self.autozoom = False
		if self.scale > self.minscale:
			self.scale = self.scale - 0.1
			self.drawarea.set_size_request(int(self.width*self.scale), int(self.height*self.scale))
			self.refresh_preview()
		self.set_bestfitmode(False)

	def set_bestfitmode(self, newstatus):
		self.bestfit_active = newstatus
		self.button_bestfit.set_active(newstatus)
		self.refresh_preview()

	def on_expose(self, widget, event):
		self.i += 1
		print self.i
		cr = widget.window.cairo_create()
		cr.set_source_rgb(1, 1, 1)
		cr.translate(0, 0)
		if self.bestfit_active: # I'm not getting loops anymore - lets try this out for a while
			self.scale = (self.drawarea.get_parent().get_allocation().width-10.0) / self.width
			self.drawarea.set_size_request(int(self.width*self.scale), int(self.height*self.scale))
		if self.scale != 1:
			cr.scale(self.scale, self.scale)
		cr.rectangle(0, 0, self.width, self.height)
		cr.fill()
		self.current_page.render(cr)
		self.autozoom = True
