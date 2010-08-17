/**
 * AppConfig.cpp
 *
 * Copyright (C) 2010 -  Wei-Ning Huang (AZ) <aitjcize@gmail.com>
 * All Rights reserved.
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software Foundation,
 * Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
 */

#ifdef HAVE_CONFIG_H
# include "config.h"
#endif

#include "AppConfig.h"

void AppConfig::set_default() {
  // Editor section
  line_numbers = true;
  highlighting = true;
  textwrapping = true;
  wordwrapping = true;
  spelling = false;
  toolbar = true;
  statusbar = true;
  rightpane = true;
  spell_language = "None";
  font = "Monospace 10";

  // File section
  autosaving = false;
  autosave_timer = 600;

  // Compile section
  compile_status = true;
  typesetter = "pdflatex";
  compile_scheme = "on_idle";
  compile_timer = 1;
  idle_threshold = 2000;

  // Misc section
  recent1 = NULL;
  recent2 = NULL;
  recent3 = NULL;
  welcome = "\\documentclass{article}\n\\begin{document}\n\\begin{center}\n"
"\\Huge{Welcome to Gummi} \\\\\\\n\\\\\n\\LARGE{You are using the " + PACKAGE_VERSION + " version.\\\\\nI welcome your suggestions at\\\\\nhttp://gummi.midnightcoding.org}\\\\\n\\end{center}\n\\end{document}";
  sync(1);
}

void AppConfig::sync(bool status) {
  GROUP    ( Editor ); 
  SYNC_BOOL( line_numbers );
  SYNC_BOOL( highlighting );
  SYNC_BOOL( textwrapping );
  SYNC_BOOL( wordwrapping );
  SYNC_BOOL( spelling );
  SYNC_BOOL( toolbar );
  SYNC_BOOL( statusbar );
  SYNC_BOOL( rightpane );
  SYNC_STR ( spell_language );
  SYNC_STR ( font );

  GROUP    ( File );
  SYNC_BOOL( autosaving );
  SYNC_INT ( autosave_timer );

  GROUP    ( Compile );
  SYNC_BOOL( compile_status );
  SYNC_STR ( typesetter );
  SYNC_STR ( compile_scheme );
  SYNC_INT ( compile_timer );
  SYNC_INT ( idle_threshold );
  
  GROUP    ( Misc );
  SYNC_STR ( recent1 );
  SYNC_STR ( recent2 );
  SYNC_STR ( recent3 );
  SYNC_STR ( welcome );
}
