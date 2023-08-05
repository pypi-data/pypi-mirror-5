import warnings
from .platform import PLATFORM, OSX, LINUX
from os import path


IMAGES_DIR = path.join(path.dirname(__file__), 'images')


def get_icon_name(success):
    name = 'ok' if success else 'error'
    return 'dialog-%s' % name

def get_icon(success):
    """
    Returns icon as binary data depending on given ``success`` boolean.
    """
    icon_name = get_icon_name(success)
    return open(path.join(IMAGES_DIR, '%s.png' % icon_name), 'rb').read()


def notify(sender, title, message, success):
    if PLATFORM == OSX:
        try:
            from gntp.notifier import mini
            mini(message, sender, title=title, notificationIcon=get_icon(success))
        except ImportError:
            warnings.warn('Could not import gntp. Please install it to see alerts')
    elif PLATFORM == LINUX:
        try:
            import pynotify
            pynotify.init('nosetests')
            icon_name = get_icon_name(success)
            notification = pynotify.Notification(title, message, icon_name)
            notification.show()
        except ImportError:
            warnings.warn('Could not import pynotify. '
                'Please install libnotify to see alerts')


class Notification(object):

    def __init__(self, sender='Tests', total=0, fails=0, errors=0):
        self.sender = sender
        self.total = total
        self.fails = fails
        self.errors = errors

        self.notify = notify

    def __repr__(self):
        return '<Notification: %d/%d >' % (self.problems, self.total)

    def __eq__(self, other):
        return all([
            self.sender == other.sender,
            self.fails == other.fails,
            self.errors == other.errors,
            self.total == other.total,
        ])

    @property
    def problems(self):
        return self.fails + self.errors

    def get_message(self):
        if self.problems:
            return '%d out of %d tests failed!' % (self.problems, self.total)
        else:
            return 'All %d tests passed.' % self.total

    def get_title(self):
        if self.problems:
            return 'Failed'
        else:
            return 'Success'

    def send(self):
        """
        Sends this notification to underlying notification center.
        """
        self.notify(
            sender=self.sender,
            title=self.get_title(),
            message=self.get_message(),
            success=self.problems == 0,
        )

