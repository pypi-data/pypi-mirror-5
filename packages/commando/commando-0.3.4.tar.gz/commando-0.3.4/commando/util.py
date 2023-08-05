"""
Logging and other aspects.
"""

# pylint: disable-msg=C0103

import logging
import sys

from logging import NullHandler
from subprocess import check_call, check_output, Popen

class CommandoLoaderException(Exception):
    """
    Exception raised when `load_python_object` fails.
    """
    pass

def load_python_object(name):
    """
    Loads a python module from string
    """
    logger = getLoggerWithNullHandler('commando.load_python_object')
    (module_name, _, object_name) = name.rpartition(".")
    if module_name == '':
        (module_name, object_name) = (object_name, module_name)
    try:
        logger.debug('Loading module [%s]' % module_name)
        module = __import__(module_name)
    except ImportError:
        raise CommandoLoaderException(
                "Module [%s] cannot be loaded." % module_name)

    if object_name == '':
        return module

    try:
        module = sys.modules[module_name]
    except KeyError:
        raise CommandoLoaderException(
                "Error occured when loading module [%s]" % module_name)

    try:
        logger.debug('Getting object [%s] from module [%s]' %
                    (object_name, module_name))
        return getattr(module, object_name)
    except AttributeError:
        raise CommandoLoaderException(
                "Cannot load object [%s]. "
                "Module [%s] does not contain object [%s]. "
                "Please fix the configuration or "
                "ensure that the module is installed properly" %
                    (
                        name,
                        module_name,
                        object_name
                    )
        )


class ShellCommand(object):
    """
    Provides a simpler interface for calling shell commands.
    Wraps `subprocess`.
    """

    def __init__(self, cwd=None, cmd=None):
        self.cwd = cwd
        self.cmd = cmd

    def __process__(self, *args, **kwargs):

        if self.cmd and not kwargs.get('shell', False):
            new_args = [self.cmd]
            new_args.extend(args)
            args = new_args

        args = [arg for arg in args if arg]

        if self.cwd and 'cwd' not in kwargs:
            kwargs['cwd'] = self.cwd

        return (args, kwargs)

    def call(self, *args, **kwargs):
        """
        Delegates to `subprocess.check_call`.
        """
        args, kwargs = self.__process__(*args, **kwargs)
        return check_call(args, **kwargs)

    def get(self, *args, **kwargs):
        """
        Delegates to `subprocess.check_output`.
        """
        args, kwargs = self.__process__(*args, **kwargs)
        return check_output(args, **kwargs)

    def open(self, *args, **kwargs):
        """
        Delegates to `subprocess.Popen`.
        """
        args, kwargs = self.__process__(*args, **kwargs)
        return Popen(args, **kwargs)


def getLoggerWithConsoleHandler(logger_name=None):
    """
    Gets a logger object with a pre-initialized console handler.
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        if sys.platform == 'win32':
            formatter = logging.Formatter(
                            fmt="%(asctime)s %(name)s %(message)s",
                            datefmt='%H:%M:%S')
        else:
            formatter = ColorFormatter(fmt="$RESET %(asctime)s "
                                      "$BOLD$COLOR%(name)s$RESET "
                                      "%(message)s", datefmt='%H:%M:%S')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


def getLoggerWithNullHandler(logger_name):
    """
    Gets the logger initialized with the `logger_name`
    and a NullHandler.
    """
    logger = logging.getLogger(logger_name)
    if not logger.handlers:
        logger.addHandler(NullHandler())
    return logger


## Code stolen from :
## http://stackoverflow.com/q/384076
##
BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

COLORS = {
    'WARNING': YELLOW,
    'INFO': WHITE,
    'DEBUG': BLUE,
    'CRITICAL': YELLOW,
    'ERROR': RED,
    'RED': RED,
    'GREEN': GREEN,
    'YELLOW': YELLOW,
    'BLUE': BLUE,
    'MAGENTA': MAGENTA,
    'CYAN': CYAN,
    'WHITE': WHITE,
}

RESET_SEQ = "\033[0m"       # pylint: disable-msg=W1401
COLOR_SEQ = "\033[1;%dm"    # pylint: disable-msg=W1401
BOLD_SEQ = "\033[1m"        # pylint: disable-msg=W1401


class ColorFormatter(logging.Formatter):
    """
    Basic formatter to show colorful log lines.
    """

    def __init__(self, *args, **kwargs):
        # can't do super(...) here because Formatter is an old school class
        logging.Formatter.__init__(self, *args, **kwargs)

    def format(self, record):
        levelname = record.levelname
        color = COLOR_SEQ % (30 + COLORS[levelname])
        message = logging.Formatter.format(self, record)
        message = message.replace("$RESET", RESET_SEQ)\
                           .replace("$BOLD",  BOLD_SEQ)\
                           .replace("$COLOR", color)

        for key, value in COLORS.items():
            message = message.replace("$" + key, COLOR_SEQ % (value + 30))\
                             .replace("$BG" + key, COLOR_SEQ % (value + 40))\
                             .replace("$BG-" + key, COLOR_SEQ % (value + 40))
        return message + RESET_SEQ

logging.ColorFormatter = ColorFormatter


__all__ = [
            'CommandoLoaderException',
            'load_python_object',
            'ShellCommand',
            'ColorFormatter',
            'getLoggerWithNullHandler',
            'getLoggerWithConsoleHandler'
        ]