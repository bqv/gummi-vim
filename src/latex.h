/**
 * @file   latex.h
 * @brief   
 *
 * Copyright (C) 2010 Gummi-Dev Team <alexvandermey@gmail.com>
 * All Rights reserved.
 * 
 * Permission is hereby granted, free of charge, to any person
 * obtaining a copy of this software and associated documentation
 * files (the "Software"), to deal in the Software without
 * restriction, including without limitation the rights to use,
 * copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the
 * Software is furnished to do so, subject to the following
 * conditions:
 *
 * The above copyright notice and this permission notice shall be
 * included in all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
 * OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 * NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
 * HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
 * WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
 * OTHER DEALINGS IN THE SOFTWARE.
 */

#ifndef __GUMMI_LATEX_H__
#define __GUMMI_LATEX_H__

#include <glib.h>

#include "editor.h"
#include "gui/gui-preview.h"

#define GU_LATEX(x) ((GuLatex*)x)
typedef struct _GuLatex GuLatex;

struct _GuLatex {
    gchar* typesetter;
    /* use fixed size for errorlines in consider of performance */
    gint errorlines[BUFSIZ];
    gchar* errormessage;
    gboolean modified_since_compile;
};

GuLatex* latex_init (void);
void latex_update_workfile (GuLatex* mc, GuEditor* ec);
void latex_update_pdffile (GuLatex* mc, GuEditor* ec);
void latex_update_auxfile (GuLatex* mc, GuEditor* ec);
void latex_export_pdffile (GuLatex* lc, GuEditor* ec, const gchar* path,
        gboolean prompt_overrite);

#endif /* __GUMMI_LATEX_H__ */
