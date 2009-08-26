#!/usr/bin/env python

from distutils.core import setup
import sys

_data_files = [
	('share/applications', ['gummi/misc/gummi.desktop']),
	('share/pixmaps', ['gummi/misc/gummi.png'])	
	]

files = ["gummi.xml",
	 "docs/CHANGES", 
	 "docs/LICENSE",
	 "docs/INSTALL",
	 "gui/gummi.xml",
	 "gui/prefs.xml",
	 "gui/icon.png"
	]

setup(
	name = 'gummi',
	version = '0.1f',
	summary = 'Simple LaTeX editor',
	description = 'Simple LaTex editor for GTK users',
	author = 'Alexander van der Mey',
	author_email = 'alexvandermey@gmail.com',
	url = 'http://code.google.com/p/gummi/',
	license = 'MIT/Beerware',
    	packages = ['gummi'],
	package_data = {'gummi' : files },
	scripts = ['gummi/misc/gummi'],
	data_files = _data_files,
)

