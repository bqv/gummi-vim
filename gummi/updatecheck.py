
# --------------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <alexvandermey@gmail.com> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return -Alexander van der Mey
# --------------------------------------------------------------------------------

import gtk
import urllib


class updatecheck:
	
	def __init__(self, parent):
		self.parent = parent
		self.url = urllib.urlopen("http://gummi.googlecode.com/svn/trunk/dev/latest")
		latest = str(self.url.readline())
		
		message = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_INFO, gtk.BUTTONS_NONE, 
		"Currently installed:\n" + parent.version + "\n\nCurrently available:\n" + latest)
		message.add_button(gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE)
		message.set_title("Update Check")
		resp = message.run()
		if resp == gtk.RESPONSE_CLOSE:
			message.destroy()




