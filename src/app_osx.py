# coding: utf-8
import os
import threading
import webbrowser
import Foundation

import requests
import rumps

import consts
import tw_auth

# DEBUG purposes
# rumps.rumps._NOTIFICATIONS = False


class App(rumps.App):
    def __init__(self):
        super(App, self).__init__('Whale', quit_button=None)
        self.menu = ['Channels', rumps.separator, "Preferences", rumps.separator, 'Quit']
        self.icon = os.path.join(consts.RESOURCES_PATH, 'online.png')

        self.channels = []

        # OS X Cocoa user preferences
        self.user_defaults = Foundation.NSUserDefaults.standardUserDefaults()

        self.session = None
        self.watch_timer = None

        self.authenticate()

    def authenticate(self):
        """Begin Twitch.tv authentication process.
        Auth requests handler work in his own thread so it won't block entire program.

        :return:
        """
        access_token = self.user_defaults.stringForKey_(consts.TWITCH_ACCESS_TOKEN)
        if not access_token:
            ts = tw_auth.TokenHandler()
            auth_thread = threading.Thread(target=ts.get_access_token, args=(self.auth_callback, ))
            auth_thread.start()
        else:
            self.auth_callback(access_token=access_token, error=None)

    def auth_callback(self, access_token, error):
        """Callback function called after Twitch OAuth Authentication.

        :param access_token: access token
        :type access_token: str or None
        :param error: error
        :type error: str or None
        :return: None
        """
        # Check for auth errors
        if error:
            rumps.notification('Whale', 'Error', 'Twitch.tv authentication failed')
            return

        self.user_defaults.setValue_forKey_(access_token, consts.TWITCH_ACCESS_TOKEN)
        self.user_defaults.synchronize()

        print 'Token successfullly updated'

        self.init_twitch_session()

        user_dict = self.load_user_info()
        self.load_user_followings(user_dict['name'])

    def init_twitch_session(self):
        if not self.session:
            self.session = requests.session()

        self.session.headers.update({'Client-ID': tw_auth.TWITCH_CLIENT_ID})
        self.session.headers.update({'Authorization': 'OAuth ' +
                                                      self.user_defaults.stringForKey_(consts.TWITCH_ACCESS_TOKEN)})

    def load_user_info(self):
        response = self.session.get('https://api.twitch.tv/kraken/user', verify=False)
        if response.status_code == 200:
            try:
                return response.json()
            except Exception as e:
                print e
                return None

    def load_user_followings(self, user_name):
        """Load user following from Twitch.tv API

        :return:
        """
        print 'Begin load user follows'
        response = self.session.get('https://api.twitch.tv/kraken/users/%s/follows/channels' % user_name, verify=False)
        if response.status_code == 200:
            try:
                response_json = response.json()
            except Exception as e:
                print e
                return

            for follow in response_json['follows']:
                channel = follow.get('channel')

                menu_item = rumps.MenuItem(
                    title=channel['display_name'],
                    key=channel['name'],
                    icon=consts.Images.offline,
                    callback=self.channel_action
                )

                self.channels.append(menu_item)

            self.menu['Channels'].update(self.channels)

            self.begin_watch()
            # self.check_channels_status()



    @rumps.clicked("Preferences")
    def prefs(self, sender):
        # Foundation.NSWorkspace.sharedWorkspace().openFile_(url)
        rumps.notification(consts.WHALE_TITLE, '', 'Preferences are not implemented at the moment')

    @rumps.clicked('Quit')
    def quit(self, sender):
        print 'Quit', sender
        if self.watch_timer and self.watch_timer.is_alive():
            self.watch_timer.stop()
        rumps.quit_application()

    def channel_action(self, sender):
        """

        :param sender:
        :type sender: :class:`rumps.MenuItem`
        :return:
        """
        url = 'https://twitch.tv/%s' % sender.key
        webbrowser.open(url)

    def begin_watch(self):
        print 'Begin begin_watch'

        check_interval = self.user_defaults.floatForKey_(consts.CHECK_INTERVAL) or 900  # set value to 15 minutes

        print 'Begin watching channels every ', check_interval,  ' sec'

        self.watch_timer = rumps.Timer(callback=self.check_channels_status, interval=check_interval)
        self.watch_timer.start()

    def check_channels_status(self, sender):
        print 'Begin check_channels_status by %s' % sender

        for channel in self.channels:
            if self.menu['Channels'].has_key(channel.key):
                self.check_channel_status(channel.key)

    def check_channel_status(self, channel_name):
        channel_url = 'https://api.twitch.tv/kraken/streams/{channel_name}'.format(channel_name=channel_name)
        print 'check stream at ', channel_url

        response = self.session.get(channel_url, verify=False)
        if response.status_code == 200:
            stream_json = response.json()
            stream = stream_json.get('stream')

            # Check prev state icon and new stream state. If it changes to online that user should be notified
            if self.user_defaults.boolForKey_(consts.ALLOW_USER_NOTIFICATION) \
                and self.menu['Channels'][channel_name].icon == consts.Images.offline \
                and stream:
                    rumps.notification(
                        consts.WHALE_TITLE,
                        'Channel online!',
                        '%s is online now' % self.menu['Channels'][channel_name].title
                    )

            print '%s is active? %s' % (channel_name, True if stream else False)
            self.menu['Channels'][channel_name].set_icon(consts.Images.app if stream else consts.Images.offline)
