from os.path import expanduser

from configparser import ConfigParser

import json

from urllib.request import urlopen
from urllib.parse import urljoin, urlencode

class PyloadConnection:

    def __init__(self):
        config = ConfigParser()
        config.read(expanduser("~/.pyloadutils"))

        self.url_base = urljoin(config.get('base', 'host'), 'api/')

        user = config.get('base', 'user')
        password = config.get('base', 'password')

        self.session = self._call('login', {'username': user, 'password': password}, False)

    def _call(self, name, args={}, encode=True):
        url = urljoin(self.url_base, name)

        if encode:
            data = {}

            for key, value in args.items():
                data[key] = json.dumps(value)
        else:
            data = args

        if hasattr(self, 'session'):
            data['session'] = self.session

        post = urlencode(data).encode('utf-8')

        return json.loads(urlopen(url, post).read().decode('utf-8'))

    def __getattr__(self, name):
        def wrapper(**kargs):
            return self._call(name, kargs)

        return wrapper
