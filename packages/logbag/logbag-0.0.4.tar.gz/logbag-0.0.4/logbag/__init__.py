import urllib2
from threading import Thread
from urllib import urlencode


def stuff(url, user, log, level, message, **kwargs):
    data = kwargs
    data.update({
        'user': user,
        'log': log,
        'level': level,
        'message': message
    })
    for k, v in data.iteritems():
        if isinstance(data[k], unicode):
            data[k] = v.encode('utf-8')
    urllib2.urlopen(url, urlencode(data))


class Logger(object):
    def __init__(self, url, user, log):
        self._url = url
        self._user = user
        self._log = log

    def log(self, level, message, **kwargs):
        """
        Thread wrapper for stuff
        """
        thread = Thread(
            target=stuff,
            args=(self._url, self._user, self._log, level, message),
            kwargs=kwargs
            )
        thread.start()

    def debug(self, message, **kwargs):
        self.log('debug', message, **kwargs)

    def info(self, message, **kwargs):
        self.log('info', message, **kwargs)

    def warning(self, message, **kwargs):
        self.log('warning', message, **kwargs)

    def error(self, message, **kwargs):
        self.log('error', message, **kwargs)

    def critical(self, message, **kwargs):
        self.log('critical', message, **kwargs)

