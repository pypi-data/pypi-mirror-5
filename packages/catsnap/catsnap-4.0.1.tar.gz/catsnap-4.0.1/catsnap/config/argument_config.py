from __future__ import unicode_literals

import sys
import argparse

from catsnap.config.base import Config

class ArgumentConfig(Config):
    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-e', '--extension', action='store_true',
                default=None,
                help="Append #.gif to urls (i.e. for pasting in Campfire)")
        parser.add_argument('--no-extension', action='store_false',
                dest='extension', default=None,
                help="Do no append #.gif to urls")
        parser.add_argument('--api-host', help="The host where your catsnap "
                                               "api can be found")
        parser.add_argument('--api-key', help="The the key for "
                                              "your catsnap api")
        parser.add_argument('arg', nargs='*')

        #We're manually grabbing sys.argv so the tests can easily mock it
        #We need to drop the first item because argparse will see it as an
        #argument, rather than as the script-name
        argv = sys.argv[1:]
        self._args = parser.parse_args(argv)

        for setting in self.CLIENT_SETTINGS:
            if not hasattr(self._args, setting):
                raise AttributeError(setting)

    def __getitem__(self, item):
        try:
            argument = getattr(self._args, item)
            if argument is None:
                raise KeyError(item)
            return argument
        except AttributeError:
            raise KeyError(item)

    def __contains__(self, item):
        return hasattr(self._args, item) and \
                getattr(self._args, item) is not None
