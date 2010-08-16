/**
 * Appconfig.h
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

#include <string>

#include "ConfigFile.h"

using std::string;

class AppConfig: public ConfigFile {
  public:
    AppConfig(string filePath): ConfigFile(filePath) {}
    virtual void setDefault();
    virtual void sync(bool status);

    // Editor section
    bool line_numbers;
    bool highlighting;
    bool textwrapping;
    bool wordwrapping;
    bool spelling;
    bool toolbar;
    bool statusbar;
    bool rightpane;
    const char* spell_language;
    const char* font;

    // File section
    bool autosaving;
    int autosave_timer;

    // Compile section
    bool compile_status;
    const char* typesetter;
    const char* compile_scheme;
    int compile_timer;
    int idle_threshold;
    
    // Misc section
    const char* recent1;
    const char* recent2;
    const char* recent3;
    const char* welcome;
};
