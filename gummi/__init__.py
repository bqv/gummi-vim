# Internationalization support

import gettext
import locale

LOCALE_DIR = '/usr/share/locale'

locale.setlocale(locale.LC_ALL, "")
#locale.bindtextdomain("gummi", LOCALE_DIR)

gettext.bindtextdomain("gummi", LOCALE_DIR)
gettext.textdomain("gummi")
