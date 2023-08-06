# vim: set fileencoding=utf-8 :
from __future__ import absolute_import
import logging


class NullHandler(logging.Handler):
    def emit(self, record):
        pass


def log_to_stderr(logger=None, level = logging.DEBUG):
    """Configures the python log system to log to stderr

    logger: Logger to configure. Pass none to use the root logger.

    Makes the root logger log to stderr and sets up a formatter that prints
    the date, loglevel and logger name
    """
    if logger is None:
        logger = logging.getLogger()
    else:
        logger = logging.getLogger(logger)
    logger.setLevel(logging.DEBUG)

    handler = logging.StreamHandler()
    handler.setLevel(level)

    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s|%(name)s] %(message)s')
    handler.setFormatter(formatter)

    logger.addHandler(handler)


def setup_logging(app):
    """Setup the python logging system according to whether the given app
    is in debug mode
    """
    if app.debug:
        # Configure the root logger to output on stderr
        log_to_stderr()
    else:
        # Configure the package logger to use NullHandler and avoid errors.
        # The application should set up a proper handler if it wants logging
        # in production.
        pkg_logger = logging.getLogger(__package__)
        handler = NullHandler()
        pkg_logger.addHandler(handler)
