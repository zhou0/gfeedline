#
# gfeedline - A Social Networking Client
#
# Copyright (c) 2012, Yoshizumi Endo.
# Licence: GPL3

import os
from string import Template

from constants import SHARED_DATA_FILE
from utils.settings import SETTINGS


class Theme(object):

    def __init__(self):
        self.all_themes = {}
        path = SHARED_DATA_FILE('html/theme/')

        for root, dirs, files in os.walk(path):
            for file in files:
                name = file.split('.')[0]
                ext = os.path.splitext(file)[1][1:]

                self.all_themes.setdefault(name, {})
                self.all_themes[name][ext] = os.path.join(root, file)

                if file.find('Ascending') > 0:
                    self.all_themes[name]['is_ascending'] = True

        SETTINGS.connect("changed::theme", self.on_setting_theme_changed)
        self.on_setting_theme_changed(SETTINGS, 'theme')

    def is_ascending(self):
        theme_name = self._get_theme_name()
        is_ascending = self.all_themes[theme_name].get('is_ascending')
        return bool(is_ascending)

    def get_all_list(self):
        return self.all_themes.keys()

    def get_css_file(self):
        theme_name = self._get_theme_name()
        css_file = self.all_themes[theme_name].get('css')

        if not os.path.isfile(css_file):
            css_file_old = SHARED_DATA_FILE('html/theme/Twitter.css')

        return css_file

    def _get_theme_name(self):
        return SETTINGS.get_string('theme')

    def on_setting_theme_changed(self, settings, key): # get_status_template
        theme_name = self._get_theme_name()
        template_file = self.all_themes[theme_name].get('html')

        if not os.path.isfile(template_file):
            template_file = SHARED_DATA_FILE('html/theme/Twitter.html')

        with open(template_file, 'r') as fh:
            file = fh.read()
        self.template = Template(unicode(file, 'utf-8', 'ignore'))
