/**
 * @file   motion.c
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

#include "snippets.h"
#include "latex.h"

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>

#include <glib.h>
#include <gtk/gtk.h>

#include "configfile.h"
#include "editor.h"
#include "environment.h"
#include "gui/gui-main.h"
#include "gui/gui-preview.h"
#include "latex.h"
#include "utils.h"

extern GummiGui* gui;

GuMotion* motion_init (void) {
    GuMotion* m = g_new0 (GuMotion, 1);

    m->key_press_timer = 0;
    m->signal_mutex = g_mutex_new ();
    m->compile_mutex = g_mutex_new ();
    m->compile_cv = g_cond_new ();

    return m;
}

void motion_start_compile_thread (GuMotion* m) {
    GError* err = NULL;

    m->compile_thread = g_thread_create (motion_compile_thread, m, FALSE, &err); 
    if (!m->compile_thread)
        slog (L_G_FATAL, "Can not create new thread: %s\n", err->message);
}

gboolean motion_do_compile (gpointer user) {
    L_F_DEBUG;
    GuMotion* mc = GU_MOTION (user);

    if (!g_mutex_trylock (mc->signal_mutex)) goto ret;
    g_cond_signal (mc->compile_cv);
    g_mutex_unlock (mc->signal_mutex);

ret:
    return (0 == strcmp (config_get_value ("compile_scheme"), "real_time"));
}

gpointer motion_compile_thread (gpointer data) {
    L_F_DEBUG;
    GuMotion* mc = GU_MOTION (data);
    GuEditor* editor = NULL;
    GuLatex* latex = NULL;
    GuPreviewGui* pc = NULL;
    GtkWidget* focus = NULL;
    gboolean precompile_ok;
    gchar *editortext;

    latex = gummi_get_latex ();
    pc = gui->previewgui;

    while (TRUE) {
        if (!g_mutex_trylock (mc->compile_mutex)) continue;
        slog (L_DEBUG, "Compile thread sleeping...\n");
        g_cond_wait (mc->compile_cv, mc->compile_mutex);
        slog (L_DEBUG, "Compile thread awoke.\n");

        if (!(editor = gummi_get_active_editor ())) {
            g_mutex_unlock (mc->compile_mutex);
            continue;
        }

        gdk_threads_enter ();
        focus = gtk_window_get_focus (gui->mainwindow);
        editortext = latex_update_workfile (latex, editor);
        
        precompile_ok = latex_precompile_check(editortext);
        g_free(editortext);

        gtk_widget_grab_focus (focus);
        gdk_threads_leave();

        if (!precompile_ok) {
            g_mutex_unlock (mc->compile_mutex);
            gdk_threads_enter();
            previewgui_start_error_mode (pc);
            gdk_threads_leave();
            continue;
        }
        
        latex_update_pdffile (latex, editor);
        g_mutex_unlock (mc->compile_mutex);

        /* Make sure the editor still exists after compile */
        if (editor == gummi_get_active_editor()) {
            gdk_threads_enter ();
            editor_apply_errortags (editor, latex->errorlines);
            errorbuffer_set_text (latex->errormessage);


            if (!pc->errormode && latex->errorlines[0] && !pc->uri) {
                previewgui_start_error_mode (pc);
            } else if (!latex->errorlines[0] && precompile_ok) {
                previewgui_stop_error_mode (pc);
                if (!pc->uri) previewgui_set_pdffile (pc, editor->pdffile);
            }

            previewgui_refresh (gui->previewgui);
            gdk_threads_leave ();
        }
    }
}

gboolean motion_idle_cb (gpointer user) {
    if (gui->previewgui->preview_on_idle)
        motion_do_compile (GU_MOTION (user));
    return FALSE;
}

void motion_start_timer (GuMotion* mc) {
    motion_stop_timer (mc);
    mc->key_press_timer = g_timeout_add_seconds (atoi (
                config_get_value ("compile_timer")), motion_idle_cb, mc);
}

void motion_stop_timer (GuMotion* mc) {
    if (mc->key_press_timer > 0) {
        g_source_remove (mc->key_press_timer);
        mc->key_press_timer = 0;
    }
}

gboolean on_key_press_cb (GtkWidget* widget, GdkEventKey* event, void* user) {
    motion_stop_timer (GU_MOTION (user));
    if (config_get_value("snippets") && 
        snippets_key_press_cb (gummi_get_snippets (),
                               gummi_get_active_editor (), event))
        return TRUE;
    return FALSE;
}

gboolean on_key_release_cb (GtkWidget* widget, GdkEventKey* event, void* user) {
    motion_start_timer (GU_MOTION (user));
    if (config_get_value("snippets") && 
        snippets_key_release_cb (gummi_get_snippets (),
                                 gummi_get_active_editor (), event))
        return TRUE;
    return FALSE;
}
