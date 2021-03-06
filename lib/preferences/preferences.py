#
# gfeedline - A Social Networking Client
#
# Copyright (c) 2012, Yoshizumi Endo.
# Licence: GPL3

from gi.repository import Gtk

from ..plugins.twitter.assistant import TwitterAuthAssistant
from ..utils.settings import (SETTINGS, SETTINGS_VIEW, SETTINGS_GEOMETRY, 
                              SETTINGS_DESKTOP)
from ..utils.autostart import AutoStart
from ..constants import SHARED_DATA_FILE
from ..theme import Theme
from accounts import AccountAction
from feedsource import FeedSourceAction
from filters import FilterAction

class Preferences(object):

    def __init__(self, mainwindow):
        self.window = mainwindow
        self.liststore = mainwindow.liststore

        gui = Gtk.Builder()
        gui.add_from_file(SHARED_DATA_FILE('preferences.glade'))
        self.preferences = gui.get_object('preferences')

        notebook = gui.get_object('notebook1')
        recent_page = SETTINGS.get_int('preferences-recent-page')
        notebook.set_current_page(recent_page)

        # view & desktop

        self.combobox_theme = ComboboxTheme(gui)
        self.combobox_order = ComboboxTimelineOrder(gui)
        self.fontbutton = TimeLineFontButton(gui, mainwindow)
 
#        is_other_column = SETTINGS_VIEW.get_boolean('conversation-other-column')
#        checkbutton_conversation = gui.get_object('checkbutton_conversation')
#        checkbutton_conversation.set_active(is_other_column)

        is_system_font = SETTINGS_VIEW.get_boolean('use-system-font')
        checkbutton_systtem_font = gui.get_object('checkbutton_system_font')
        checkbutton_systtem_font.set_active(is_system_font)
        self.fontbutton.set_sensitive(not is_system_font)
        SETTINGS_VIEW.connect("changed::use-system-font", 
                         self.on_settings_system_font_change)

        self.autostart = AutoStartWithCheckButton(gui, 'gfeedline')

        SETTINGS.connect("changed::window-sticky", self.on_settings_sticky_change)
        self.on_settings_sticky_change(SETTINGS, 'window-sticky')
        sticky = SETTINGS.get_boolean('window-sticky')
        checkbutton_sticky = gui.get_object('checkbutton_sticky')
        checkbutton_sticky.set_active(sticky)

        # accounts, feeds & filters

        self.account_action = AccountAction(
            gui, mainwindow, self.liststore, self.preferences)
        self.feedsource_action = FeedSourceAction(
            gui, mainwindow, self.liststore, self.preferences)
        self.filter_action = FilterAction(
            gui, mainwindow, self.liststore.filter_liststore, self.preferences)

        gui.connect_signals(self)

        self._load_prefs_size(self.preferences)
        self.preferences.show_all()

    def _load_prefs_size(self, preferences):
        w = SETTINGS_GEOMETRY.get_int('prefs-width')
        h = SETTINGS_GEOMETRY.get_int('prefs-height')
        preferences.resize(w, h)

    def _save_prefs_size(self, preferences):
        w, h = preferences.get_size()
        SETTINGS_GEOMETRY.set_int('prefs-width', w)
        SETTINGS_GEOMETRY.set_int('prefs-height', h)


    def on_settings_system_font_change(self, settings, key):
        self.window.on_menuitem_zoom_default_activate(None)

    def on_settings_sticky_change(self, settings, key):
        if settings.get_boolean(key):
            self.preferences.stick()
        else:
            self.preferences.unstick()

    def on_button_close_clicked(self, notebook):
        page = notebook.get_current_page()
        SETTINGS.set_int('preferences-recent-page', page)

        is_theme_changed = self.combobox_theme.check_active()
        is_order_changed = self.combobox_order.check_active()
        if is_theme_changed or is_order_changed:
            self.combobox_theme.update_theme()

        self.liststore.save_settings()
        self.liststore.filter_liststore.save_settings()
        self.liststore.account_liststore.save_settings()

        self._save_prefs_size(self.preferences)
        self.preferences.destroy()

    def on_checkbutton_conversation_toggled(self, button):
        is_other_column = button.get_active()
        SETTINGS_VIEW.set_boolean('conversation-other-column', is_other_column)

    def on_checkbutton_system_font_toggled(self, button):
        is_system_font = button.get_active()
        SETTINGS_VIEW.set_boolean('use-system-font', is_system_font)
        self.fontbutton.set_sensitive(not is_system_font)

    def on_checkbutton_sticky_toggled(self, button):
        sticky = button.get_active()
        SETTINGS.set_boolean('window-sticky', sticky)

    def on_checkbutton_autostart_toggled(self, button):
        state = button.get_active()
        self.autostart.set(state)


    def on_button_account_new_clicked(self, preferences):
        self.account_action.on_button_new_clicked(preferences)

    def on_button_account_prefs_clicked(self, treeselection):
        self.account_action.on_button_prefs_clicked(treeselection)

    def on_button_account_del_clicked(self, treeselection):
        self.account_action.on_button_del_clicked(treeselection)

    def on_account_treeview_cursor_changed(self, treeselection):
        self.account_action.on_treeview_cursor_changed(treeselection)


    def on_button_feed_new_clicked(self, button):
        self.feedsource_action.on_button_new_clicked(button)

    def on_button_feed_prefs_clicked(self, treeselection):
        self.feedsource_action.on_button_prefs_clicked(treeselection)

    def on_button_feed_del_clicked(self, treeselection):
        self.feedsource_action.on_button_del_clicked(treeselection)

    def on_feedsource_treeview_cursor_changed(self, treeselection):
        self.feedsource_action.on_treeview_cursor_changed(treeselection)

    def on_feedsource_treeview_query_tooltip(self, treeview, *args):
        self.feedsource_action.on_treeview_query_tooltip(treeview, args)


    def on_button_filter_new_clicked(self, button):
        self.filter_action.on_button_new_clicked(button)

    def on_button_filter_prefs_clicked(self, treeselection):
        self.filter_action.on_button_prefs_clicked(treeselection)

    def on_button_filter_del_clicked(self, treeselection):
        self.filter_action.on_button_del_clicked(treeselection)

    def on_filter_treeview_cursor_changed(self, treeselection):
        self.filter_action.on_treeview_cursor_changed(treeselection)

#    def on_filter_treeview_query_tooltip(self, treeview, *args):
#        self.filter_action.on_treeview_query_tooltip(treeview, args)


    def on_plugin_treeview_cursor_changed(self, treeview):
        pass

class ComboboxTheme(object):

    def __init__(self, gui):
        theme = Theme()
        self.labels = sorted(theme.get_all_list())

        self.combobox = gui.get_object('comboboxtext_theme')
        for text in self.labels:
            self.combobox.append_text(text)

        selected_theme = SETTINGS_VIEW.get_string('theme').decode('utf-8')
        if selected_theme not in self.labels:
            selected_theme = 'Default'

        num = self.labels.index(selected_theme)
        self.combobox.set_active(num)

    def check_active(self):
        old = SETTINGS_VIEW.get_string('theme')
        self.new = self.labels[self.combobox.get_active()]
        return old != self.new

    def update_theme(self):
        SETTINGS_VIEW.set_string('theme', self.new)

class ComboboxTimelineOrder(object):

    def __init__(self, gui):
        self.combobox = gui.get_object('comboboxtext_order')
        num = SETTINGS_VIEW.get_int('timeline-order')
        self.combobox.set_active(num)

    def check_active(self):
        num = self.combobox.get_active()

        theme = Theme()
        old = theme.is_ascending()
        new = theme.is_ascending(num)

        SETTINGS_VIEW.set_int('timeline-order', num)
        return old != new

class TimeLineFontButton(object):

    def __init__(self, gui, window):
        self.window = window
        font_name = SETTINGS_VIEW.get_string('font')

        self.widget = gui.get_object('fontbutton')
        self.widget.set_font_name(font_name)
        self.label = gui.get_object('label_font')

        SETTINGS_VIEW.connect("changed::font", self.on_settings_font_change)
        #self.on_settings_font_change(SETTINGS, 'window-sticky')

        self.widget.connect('font-set', self.on_button_font_set)

    def set_sensitive(self, state):
        self.label.set_sensitive(state)
        self.widget.set_sensitive(state)

    def on_button_font_set(self, button, *args):
        font_name = button.get_font_name()
        SETTINGS_VIEW.set_string('font', font_name)

    def on_settings_font_change(self, settings, key):
        font_css = self.window.font.zoom_default()
        self.window.change_font(font_css)

class AutoStartWithCheckButton(AutoStart):

    def __init__(self, gui, app_name):
        super(AutoStartWithCheckButton, self).__init__(app_name)

        checkbutton = gui.get_object('checkbutton_autostart')
        checkbutton.set_sensitive(self.check_enable())
        checkbutton.set_active(self.get())
