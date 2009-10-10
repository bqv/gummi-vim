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

from __future__ import division # needed for proper int devision

import gtk
import os
import poppler

# TODO: Documentation

class PreviewPane:

	def __init__(self, builder, pdffile=None):
		
		self.builder = builder
		self.drawarea = builder.get_object("preview_drawarea")
		self.toolbar = builder.get_object("preview_toolbar")
		self.prev = builder.get_object("preview_prev")
		self.next = builder.get_object("preview_next")
		self.pageinput = builder.get_object("page_input")
		self.pagelabel = builder.get_object("page_label")
		self.zoomcombo = builder.get_object("zoomcombo")

		self.drawarea.connect("expose-event", self.on_expose)
		self.prev.connect("clicked", self.prev_page)
		self.next.connect("clicked", self.next_page)
		self.pageinput.connect("activate", self.page_input)
		self.zoomcombo.connect("changed", self.zoom_combo)

		# TODO: get this color from the gtk-theme?
		self.drawarea.modify_bg(gtk.STATE_NORMAL,
								gtk.gdk.color_parse('#edeceb'))

		self.page_total = 0
		self.current_page = 0
		self.scale = 1.0
		self.best_fit = False
		self.fit_width = True

		self.page_ratio = None # init now so we use them later in on_expose
		self.page_width = None # to check if have been set (succesful refresh)


	def set_pdffile(self, pdffile):
		if pdffile:
			self.pdffile = pdffile
			uri = 'file://' + pdffile
			self.document = poppler.document_new_from_file(uri, None)
			self.page_total = self.document.get_n_pages()
			self.pagelabel.set_text('of ' + str(self.page_total))
			self.pageinput.set_text(str(self.current_page + 1))
			# TODO: determine page_width/page_height per page
			self.page_width, self.page_height = self.get_page().get_size()
			self.page_ratio = self.page_width / self.page_height
			self.goto_page(0)
		else:
			self.pdffile = None

	def get_page(self):
		return self.document.get_page(self.current_page)

	def refresh_preview(self):
		if not os.path.exists(self.pdffile):
			print "can't refresh without a pdf file!"
			return
		uri = 'file://' + self.pdffile
		self.document = poppler.document_new_from_file(uri, None)
		self.page_total = self.document.get_n_pages()
		if self.page_total - 1 > self.current_page:
			self.next.set_sensitive(True)
		elif self.current_page >= self.page_total:
			self.goto_page(self.page_total - 1)
		self.pagelabel.set_text('of ' + str(self.page_total))
		self.pageinput.set_text(str(self.current_page + 1))
		self.page_width, self.page_height = self.get_page().get_size()
		self.page_ratio = self.page_width / self.page_height
		self.drawarea.queue_draw()

	def on_expose(self, drawarea, data):
		cr = drawarea.window.cairo_create()
		scrollw = drawarea.get_parent().get_parent()
		vp_size = scrollw.get_allocation()
		view_height = vp_size.height
		view_width = vp_size.width
		view_ratio = view_width / view_height

		if self.best_fit or self.fit_width:
			scrollw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
			if view_ratio < self.page_ratio or self.fit_width:
				self.scale = view_width / self.page_width
			else:
				self.scale = view_height / self.page_height

		if not (self.best_fit or self.fit_width):
			scrollw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
			self.drawarea.set_size_request(int(self.page_width * self.scale),
			                               int(self.page_height * self.scale))
		elif self.fit_width:
			if abs(self.page_ratio - view_ratio) > 0.01:
				self.drawarea.set_size_request(-1, int(self.page_height *
				                                       self.scale))
		elif self.best_fit:
			self.drawarea.set_size_request(-1,
			                              int(self.page_height*self.scale)-10)

		cr.scale(self.scale, self.scale)

		cr.set_source_rgb(1, 1, 1)
		cr.rectangle(0, 0, self.page_width, self.page_height)
		cr.fill()

		self.get_page().render(cr)

	def goto_page(self, page):
		if page < 0 or page >= self.page_total:
			return

		self.current_page = page

		self.prev.set_sensitive(page > 0)
		self.next.set_sensitive(page < self.page_total - 1)
		self.pageinput.set_text(str(self.current_page + 1))

		self.page_width, self.page_height = self.get_page().get_size()
		self.drawarea.queue_draw()

	def next_page(self, button):
		self.goto_page(self.current_page + 1)

	def prev_page(self, button):
		self.goto_page(self.current_page - 1)

	def page_input(self, widget):
		pagenum = widget.get_text()
		try:
			page = int(pagenum) - 1
			if page <= 0 or page >= self.page_total:
				widget.set_text(str(self.current_page + 1))
			else:
				self.goto_page(page)
		except ValueError:
			widget.set_text(str(self.current_page + 1))

	def zoom_combo(self, widget):
		# scale values
		zoomlist = [0.50, 0.70, 0.85, 1.0, 1.25, 1.5, 2.0, 3.0, 4.0]

		zoom = widget.get_active()
		if zoom == -1:
			return

		self.best_fit = self.fit_width = False
		if zoom < 2:
			if zoom == 0: # Best Fit
				self.best_fit = True
			elif zoom == 1: # Fit Page Width
				self.fit_width = True
		else:
			self.scale = zoomlist[zoom-2]

		self.drawarea.queue_draw()

