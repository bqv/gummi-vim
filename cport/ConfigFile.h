/**
 * ConfigFile.h - Base class for managing configfiles.
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

// -------------------------------------------------------------------------- //
// @Provides: ConfigFile Base class. Write variables into config files in the
// format: "var=value"
//
// @Description: 
//   To use this class, you need to inherit class ConfigFile. You need to
// implement set_default(), sync() two pure virtual functions.
// Variables are declared within the class.
// Example:
//
// @Note: the map must use 'const char*' as Key, in order to mantain the
// sequence of settings.
//
// class Inherited: public ConfigFile {
//  public:
//    Inherited(string filePath): ConfigFile(filePath) {}
//    virtual void set_default();
//
//  // ----- Place variables here ----- //
//    int var1;
//    const char* var2;
//    bool var3;
//
// };
//
// * set_default() - In this functions, you write variables and default values.
// Example:
// void Inherited::set_default() {
//   var1 = value1;
//   var2 = value2;
//   var3 = value3;
//   ...
//   sync(1); // this is a 'must'
// }
//
// * sync() - This functions sync variables between internal vector storage
// mechanism.
// The sequence of the Macro will be the sequence in the configuration file.
//
// Example:
// void Inherited::sync(bool status) {
//   GROUP(group name); 
//   SYNC_INT( var1 );
//   SYNC_STR( var2 );
//   SYNC_BOOL( var3 );
//   ...
// }
//
// The configuration file will have the following content:
// [group name]
// var1 = value1;
// var2 = value2;
// var3 = value3;
// ...
// -------------------------------------------------------------------------- //


#ifndef CONFIGFILE_H
#define CONFIGFILE_H

#include <map>
#include <vector>
#include <string>
#include <cstdlib>
using std::string;

#define CONFIG_LINE_MAX BUFSIZ

// ----- sync macros ----- //
// status == 1: STORE
// status == 0: LOAD
#define GROUP( name ) GET_CONFIG(name) = "__GROUP__"
#define SYNC_INT( name ) if (status) _STORE_INT(name);\
                          else _LOAD_INT(name);
#define SYNC_LONG( name ) if (status) _STORE_LONG(name);\
                          else _LOAD_LONG(name);
#define SYNC_STR( name ) if (status) _STORE_STR(name);\
                          else _LOAD_STR(name);
#define SYNC_BOOL( name ) if (status) _STORE_BOOL(name);\
                          else _LOAD_STR(name);

// ----- auxiliary macros ----- //
#define GET_CONFIG( name ) value_buf[find_index(#name)]
// STORE
#define _STORE_INT( name )  GET_CONFIG(name) = litoa(name)
#define _STORE_LONG( name )  GET_CONFIG(name) = litoa(name)
#define _STORE_STR( name )  GET_CONFIG(name) = (name == NULL)? "__NULL__": name
#define _STORE_BOOL( name )  GET_CONFIG(name) = (name == true)? "True": "False"
// LOAD
#define _LOAD_INT( name )  name = atoi(GET_CONFIG(name).c_str())
#define _LOAD_LONG( name )  name = atol(GET_CONFIG(name).c_str())
#define _LOAD_STR( name )  name = (GET_CONFIG(name) == "__NULL__")?\
                                     0: GET_CONFIG(name).c_str()
#define _LOAD_BOOL( name )  name = (GET_CONFIG(name) == "True"? 1: 0)

class ConfigFile {
  public:
    ConfigFile(string filePath): m_filePath(filePath) {}
    void load();
    void save();
    virtual void set_default() = 0;

  protected:
    std::vector<string> key_buf;
    std::vector<string> value_buf;
    string m_filePath;
    virtual void sync(bool status) = 0;
    const char* litoa(long long int num);
    int find_index(const char* key);
};

#endif
