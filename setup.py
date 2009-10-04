#!/usr/bin/env python

from distutils.core import setup

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
	version = '0.3.9',
	summary = 'Simple LaTeX editor',
	description = 'Simple LaTeX editor for GTK users',
	author = 'Alexander van der Mey',
	author_email = 'alexvandermey@gmail.com',
	url = 'http://gummi.googlecode.com',
	license = 'MIT',
    	packages = ['gummi'],
	package_data = {'gummi' : files },
	scripts = ['gummi/misc/gummi'],
	data_files = _data_files,
)

