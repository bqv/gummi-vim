
# --------------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <alexvandermey@gmail.com> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return -Alexander van der Mey
# --------------------------------------------------------------------------------

import gtk
import urllib

import Preferences


class UpdateCheck:

	def __init__(self):
		url = urllib.urlopen(Preferences.UPDATEURL)
		latest = str(url.readline())
		
		message = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_INFO, gtk.BUTTONS_NONE, 
		"Currently installed:\n" + Preferences.VERSION + "\n\nCurrently available:\n" + latest)
		message.add_button(gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE)
		message.set_title("Update Check")
		resp = message.run()
		if resp == gtk.RESPONSE_CLOSE:
			message.destroy()





