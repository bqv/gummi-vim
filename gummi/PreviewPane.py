#!/usr/bin/python
# -*- encoding: utf-8 -*-

from __future__ import division # needed for proper int devision

import gtk
import os
import poppler

# TODO: Documentation

class PreviewPane:

	def __init__(self, drawarea, toolbar, pdffile=None):
		self.drawarea = drawarea
		self.drawarea.connect("expose-event", self.on_expose)
		# TODO: get this color from the gtk-theme?
		self.drawarea.modify_bg(gtk.STATE_NORMAL,
								gtk.gdk.color_parse('#edeceb'))

		self.page_total = 0
		self.current_page = 0

		self.toolbar = toolbar
		self.prev = toolbar.get_nth_item(0)
		self.prev.connect("clicked", self.prev_page)
		self.prev.set_sensitive(False)
		self.next = toolbar.get_nth_item(1)
		self.next.connect("clicked", self.next_page)
		self.next.set_sensitive(False)

		# TODO: This is ugly!, suggestions?
		self.pageinput = toolbar.get_nth_item(3).get_child().get_children()[0]
		self.pageinput.connect("activate", self.page_input)
		self.pagelabel = toolbar.get_nth_item(3).get_child().get_children()[1]
		combobox_area = toolbar.get_nth_item(5)
		# stop the ugliness right here!

		# TODO: Can be done better?
		self.zoomcombo = gtk.combo_box_new_text()
		combobox_area.add(self.zoomcombo)
		self.zoomcombo.append_text('Best Fit')
		self.zoomcombo.append_text('Fit Page Width')
		self.zoomcombo.append_text('50%')
		self.zoomcombo.append_text('70%')
		self.zoomcombo.append_text('85%')
		self.zoomcombo.append_text('100%')
		self.zoomcombo.append_text('125%')
		self.zoomcombo.append_text('150%')
		self.zoomcombo.append_text('200%')
		self.zoomcombo.append_text('300%')
		self.zoomcombo.append_text('400%')
		self.zoomcombo.set_active(0)
		self.zoomcombo.show()

		self.zoomcombo.connect("changed", self.zoom_combo)

		self.scale = 1.0
		self.best_fit = True
		self.fit_width = False

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
			# TODO: move current page to a valid page?
			self.currentpage = 0
			self.prev.set_sensitive(False)

			if self.page_total <= 1:
				self.next.set_sensitive(False)
			else:
				self.next.set_sensitive(True)

		else:
			self.pdffile = None

	def get_page(self):
		return self.document.get_page(self.current_page)

	def refresh_preview(self):
		uri = 'file://' + self.pdffile
		self.document = poppler.document_new_from_file(uri, None)
		self.page_total = self.document.get_n_pages()
		self.pagelabel.set_text('of ' + str(self.page_total))
		self.pageinput.set_text(str(self.current_page + 1))
		self.page_width, self.page_height = self.get_page().get_size()
		self.page_ratio = self.page_width / self.page_height
		self.drawarea.queue_draw()

	def on_expose(self, drawarea, data):
		cr = drawarea.window.cairo_create()

		vp_size = drawarea.get_parent().get_allocation()
		view_height = vp_size.height
		view_width = vp_size.width
		view_ratio = view_width / view_height

		if self.best_fit or self.fit_width:
			if view_ratio < self.page_ratio or self.fit_width:
				self.scale = view_width / self.page_width
			else:
				self.scale = view_height / self.page_height

		if not (self.best_fit or self.fit_width):
			self.drawarea.set_size_request(int(self.page_width * self.scale),
										   int(self.page_height * self.scale))
		elif self.fit_width:
			if abs(self.page_ratio - view_ratio) > 0.01:
				self.drawarea.set_size_request(-1,int(self.page_height *
													  self.scale))

		cr.scale(self.scale, self.scale)

		cr.set_source_rgb(1, 1, 1)
		cr.rectangle(0, 0, self.page_width, self.page_height)
		cr.fill()

		self.get_page().render(cr)

	def goto_page(self, page):
		if page <= 0:
			self.prev.set_sensitive(False)
		else:
			self.prev.set_sensitive(True)

		if page >= self.page_total - 1:
			self.next.set_sensitive(False)
		else:
			self.next.set_sensitive(True)

		if page < 0 or page >= self.page_total:
			return

		self.current_page = page

		self.page_width, self.page_height = self.get_page().get_size()
		self.pageinput.set_text(str(self.current_page + 1))

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
		scrollw = self.drawarea.get_parent().get_parent()
		scrollw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		if zoom < 2:
			if zoom == 0: # Best Fit
				scrollw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_NEVER)
				self.best_fit = True
			elif zoom == 1: # Fit Page Width
				scrollw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
				self.fit_width = True
		else:
			self.scale = zoomlist[zoom-2]

		self.drawarea.queue_draw()

