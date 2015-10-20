# coding: utf-8
import ConfigParser
import os
import logging

import Foundation


RESOURCES_PATH = Foundation.NSBundle.mainBundle().resourcePath()
APP_IMAGE = os.path.join(RESOURCES_PATH, 'app.png')
OFFLINE_IMAGE = os.path.join(RESOURCES_PATH, 'offline.png')


class Config(object):
    def __init__(self):
        self.logger = logging.getLogger()
        self.logger.debug('Config initialized')

        self.parser = ConfigParser.RawConfigParser()
        self.config_file = os.path.join(RESOURCES_PATH, 'whale.ini')

    def load(self, config_file=None):
        if config_file is not None:
            self.config_file = config_file

        self.parser.read(self.config_file)
        self.logger.debug('Loaded config file %s', self.config_file)

        for section in self.parser.sections():
            for param, value in self.parser.items(section=section):
                param_name = section + '_' + param
                setattr(self, param_name, value)

    def save(self, add_sections=False, add_params=False):
        for key, value in self.__dict__.items():
            if key not in ['config_file', 'parser', 'logger']:
                section = key.split('_')[0]
                param = key.lstrip(section + '_')

                if add_sections and section not in self.parser.sections():
                    self.parser.add_section(section)

                if not add_params and param not in self.parser.items(section):
                    continue

                self.parser.set(section, param, getattr(self, key, ''))
        try:
            cfg_fp = open(self.config_file, 'w+')
            self.parser.write(cfg_fp)
            print u'Config save to %s' % self.config_file
        except IOError as e:
            self.logger.error(e)
            return False


if __name__ == '__main__':

    logging.basicConfig(level=logging.DEBUG)

    prefs = Config()
    prefs.load()
    prefs.twitch_access_token = 'test_access_token'
    prefs.save(True, True)