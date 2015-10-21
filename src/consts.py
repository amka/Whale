# coding: utf-8
import collections
import os

import Foundation


__author__ = 'meamka'

RESOURCES_PATH = Foundation.NSBundle.mainBundle().resourcePath()

Images = collections.namedtuple('Images', ['app', 'offline'])
Images.app = os.path.join(RESOURCES_PATH, 'app.png')
Images.offline = os.path.join(RESOURCES_PATH, 'offline.png')

# General
WHALE_TITLE = 'Whale'
CHANNELS_MENU_TITLE = u'Channels'

# Prefs
ALLOW_USER_NOTIFICATION = 'allow_notification'
CHECK_INTERVAL = 'check_interval'
TWITCH_ACCESS_TOKEN = 'twitch_access_token'
