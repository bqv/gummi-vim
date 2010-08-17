/**
 * ConfigFile.cpp - Base class for  managing configurations.
 *
 * Copyright (C) 2010 -  Wei-Ning Huang (AZ) <aitjcize@gmail.com>
 * All Rights reserved.
 *
 * This program is free software; you can redistribute it and/or modif y
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for  more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if  not, write to the Free Software Foundation,
 * Inc., 51 Franklin Street, Fif th Floor, Boston, MA 02110-1301 USA.
 */

#include "ConfigFile.h"
#include <iostream>
#include <fstream>
#include <string>
#include <cstring>
#include <vector>
#include <cmath>

using std::string;
using std::ios;
using std::cout;
using std::endl;

void ConfigFile::load() {
  int last = 0, pos = 0;
  char configLine[CONFIG_LINE_MAX];
  char *pstr;
  std::ifstream in(m_filePath.c_str());

  while (!in.eof()) {
    in.getline(configLine, CONFIG_LINE_MAX);
    if (0 == strncmp(configLine, "\t", 1)) {
      configLine[0] = '\n';
      value_buf[last] += configLine;
      continue;
    }
    pstr = strtok(configLine, "[=]");
    if (pstr == NULL) continue;
    last = find_index(pstr);
    pstr = strtok(NULL, "=");
    if (pstr == NULL)
      value_buf[last] = ("__NULL__");
    else
      value_buf[last] = pstr;
  }
  sync(0); // load variables from vector to memory
  in.close();
}

void ConfigFile::save() {
  std::ofstream out(m_filePath.c_str(), ios::out | ios::trunc);
  int pos = 0;

  sync(1); // store variables from memory to vector
  for (int i = 0; i < key_buf.size(); ++i) {
    while (string::npos != (pos = value_buf[i].find("\n", pos + 1)))
      value_buf[i].replace(pos, 1, "\n\t");

    if (value_buf[i] == "__NULL__")
      out << ((i != 0)? "\n": "") << "[" << key_buf[i] << "]" << endl;
    else
      out << key_buf[i] << "=" << value_buf[i] << endl;
  }
  out.close();
}

int ConfigFile::find_index(const char* key) {
  int i;
  for (i = 0; i < key_buf.size(); i++)
    if (key_buf[i] == key)
      return i;
  key_buf.push_back(key);
  value_buf.push_back("__NULL__");
  return i;
}

const char* ConfigFile::litoa(long long int num) {
  static char cha[64] = "0";
  if (num == 0) return cha;
  int tmp = 0;
  tmp = (num < 0)? -num: num;
  int digits = 0;
  while (static_cast<int>(num / pow(10, digits)))
    digits++;
  for (int i = 0; i < digits; i++)
  {
    cha[digits -i -(num > 0)] = tmp % 10 +'0';
    tmp /= 10;
  }
  if (num < 0) cha[0] = '-';
  cha[digits +(num < 0)] = '\0';
  return cha;
}
