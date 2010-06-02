# Internationalization support

import gettext
import locale

LOCALE_DIR = '/usr/share/locale'

locale.setlocale(locale.LC_ALL, "")

gettext.bindtextdomain("gummi", LOCALE_DIR)
gettext.textdomain("gummi")
gettext.install("gummi", LOCALE_DIR)
