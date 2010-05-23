# Internationalization support

import gettext
import gtk.glade
import locale

LOCALE_DIR = '/usr/share/locale'

locale.setlocale(locale.LC_ALL, "")

for module in gettext, gtk.glade:
	module.bindtextdomain("gummi", LOCALE_DIR)
	module.textdomain("gummi")
