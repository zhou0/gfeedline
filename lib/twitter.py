#!/usr/bin/python
#
# gfeedline - Gnome Social Feed Reader
#
# Copyright (c) 2012, Yoshizumi Endo.
# Licence: GPL3


import sys

from BeautifulSoup import BeautifulStoneSoup
from usercolor import UserColor

import dateutil.parser
from gi.repository import GLib
from twittytwister import twitter
from oauth import oauth

from twittytwister import streaming, txml

consumer = oauth.OAuthConsumer(sys.argv[1], sys.argv[2])
token = oauth.OAuthToken(sys.argv[3], sys.argv[4])

user_color = UserColor()


class Twitter(twitter.Twitter):

    def list_timeline(self, delegate, params={}, extra_args=None):
        return self.__get('/1/lists/statuses.xml',
                delegate, params, txml.Statuses, extra_args=extra_args)

class TwitterFeed(twitter.TwitterFeed):

    def userstream(self, delegate, args=None):
        return self._rtfeed('https://userstream.twitter.com/2/user.json',
                            delegate, args)

TwitterOauth = Twitter(consumer=consumer, token=token)
TwitterFeedOauth = TwitterFeed(consumer=consumer, token=token)


class TwitterTime(object):

    def __init__(self, utc_str):
        dt = dateutil.parser.parse(utc_str)
        self.datetime = dt.replace(tzinfo=dateutil.tz.tzutc()
                                   ).astimezone(dateutil.tz.tzlocal())

    def get_local_time(self):
        return self.datetime.strftime('%H:%M:%S')

class TwitterAPI(object):

    def __init__(self, api, view=None, params={}):
        self.all_entries = []
        self.last_id = 0
        self.view = view.webview
        self.api = api
        self.params = params

    def got_entry(self, msg, *args):
        self.all_entries.append(msg)

    def conv(self, text):
        return BeautifulStoneSoup(
            text, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)

    def print_all_entries(self):
        for entry in reversed(self.all_entries):
            self.print_entry(entry)
        self.all_entries = []

    def print_entry(self, entry):
        time = TwitterTime(entry.created_at)

        text = ("<div style='line-height: 1.4;'>"
                "<span style='color: gray'>(%s)</span> "
                "<img src=%s> "
                "<span style='color: #%s; font-weight: bold;'>%s</span> " 
                "%s"
                "</div>"
                ) % (
            time.get_local_time(), 
            entry.user.profile_image_url.replace('_normal.', '_mini.'),
            user_color.get(entry.user.id), entry.user.screen_name,  
            self.conv(entry.text))

        #print text
        self.last_id = entry.id
        self.view.update(text)

    def error(self, e):
        print e

    def start(self, interval=180):

        if self.last_id:
            self.params['since_id'] = str(self.last_id)

        api = self.api(self.got_entry, params=self.params)
        api.addErrback(self.error).addBoth(lambda x: self.print_all_entries())

        print TwitterOauth.rate_limit_remaining
        # print TwitterOauth.rate_limit_limit
        # print TwitterOauth.rate_limit_reset

        GLib.timeout_add_seconds(interval, self.start, interval)

class TwitterFeedAPI(TwitterAPI):

    def got_entry(self, msg, *args):
        self.print_entry(msg)

    def conv(self, text):
        return text

    def start(self, interval=False):
        self.api(self.got_entry, self.params).\
            addErrback(self.error)#.\
#            addBoth(lambda x: self.print_entry())
