# -*- coding: utf-8 -*-
# Copyright (c) 2010-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from cgi import escape
from datetime import datetime
import collections
import logging
import sys

from zExceptions.ExceptionFormatter import format_exception
from zope.browser.interfaces import IView
from zope.interface import Interface
from five import grok

from infrae.wsgi.utils import reconstruct_url_from_environ

logger = logging.getLogger('infrae.wsgi')


def object_name(obj):
    """Return an object name
    """
    return '%s.%s' % (obj.__class__.__module__, obj.__class__.__name__)


def object_path(obj):
    """Return an object path in the Zope database.
    """
    try:
        if hasattr(obj, 'getPhysicalPath'):
            return '/'.join(obj.getPhysicalPath())
    except:
        pass
    return 'n/a'


def log_invalid_response_data(data, environ):
    """Log an invalid response type from application. Data sent must
    always be a string (unicode strings are accepted), if it is not an
    IResult or IStreamIterator object (those must behave correctly).
    """
    logger.error(
        "Invalid response data of type %s for url '%s'" %
        (object_name(data), reconstruct_url_from_environ(environ)))


class ErrorLogView(grok.View):
    grok.context(Interface)
    grok.name('errorlog.html')
    grok.require('zope2.ViewManagementScreens')

    def update(self):
        if 'ignore_errors_update' in self.request.form:
            reporter.ignored_errors = self.request.form.get(
                'ignore_errors', [])

        self.all_errors = reporter.all_ignored_errors
        self.ignored_errors = reporter.ignored_errors
        self.errors = reporter.get_last_errors()
        self.debug_mode = self.request.response.debug_mode


class ErrorSupplement(object):
    """Add more information about an error on a view in a traceback.
    """

    def __init__(self, cls):
        self.context = cls
        if IView.providedBy(cls):
            self.context = cls.context
        self.cls = cls

    def getInfo(self, as_html=0):
        info = list()
        info.append((u'Published class', object_name(self.cls),))
        info.append((u'Object path', object_path(self.context),))
        info.append(
            (u'Object type', getattr(self.context, 'meta_type', u'n/a',)))
        if not as_html:
            return '   - ' + '\n   - '.join(map(lambda x: '%s: %s' % x, info))

        return u'<p>Extra information:<br /><li>%s</li></p>' % ''.join(map(
                lambda x: u'<li><b>%s</b>: %s</li>' % (
                    escape(str(x[0])), escape(str(x[1]))),
                info))


class ErrorReporter(object):
    """Utility to help error reporting.
    """
    all_ignored_errors = [
        'NotFound', 'Redirect',
        'Unauthorized', 'Forbidden',
        'BadRequest', 'BrokenReferenceError']

    def __init__(self, subscribed=[]):
        self.__last_errors = collections.deque([], 25)
        self.__ignore_errors = set(self.all_ignored_errors)
        self.__subscribed = list(subscribed) + [self._subscriber]

    def _subscriber(self, request, response, obj, error_info, short_message, full_traceback, extra):
        log_entry = ['\n']

        if extra is not None:
            log_entry.append(extra + '\n')

        if obj is not None:
            log_entry.append('Object class: %s\n' % object_name(obj))
            log_entry.append('Object path: %s\n' % object_path(obj))

        def log_request_info(title, key):
            value = request.get(key, 'n/a') or 'n/a'
            log_entry.append('%s: %s\n' % (title, value))

        log_request_info('Request URL', 'URL')
        log_request_info('Request method', 'method')
        log_request_info('Query string', 'QUERY_STRING')
        log_request_info('User', 'AUTHENTICATED_USER')
        log_request_info('User-agent', 'HTTP_USER_AGENT')
        log_request_info('Refer', 'HTTP_REFERER')

        log_entry.extend(full_traceback)

        # Save error.
        report = ''.join(log_entry)
        logger.error(report)
        self.__last_errors.append(
            {'url': request['URL'], 'report': report, 'time': datetime.now()})

    def subscribe_to_errors(self, handler):
        """Subscribe when an error happens.
        """
        self.__subscribed.append(handler)

    def show_errors(self, errors):
        """Show the given errors.
        """
        self.__ignore_errors -= set(errors)

    def ignore_errors(self, errors):
        """Ignore the given errors.
        """
        self.__ignore_errors += set(errors)

    @apply
    def ignored_errors():
        """Access currently ignored errors.
        """

        def getter(self):
            return list(self.__ignore_errors)

        def setter(self, errors):
            self.__ignore_errors = set(errors)

        return property(getter, setter)

    def is_loggable(self, error):
        """Tells you if this error is loggable.
        """
        error_name = error.__class__.__name__
        return error_name not in self.__ignore_errors

    def log_last_error(self, request, response, obj=None, extra=None):
        """Build an error report and log the last available error.
        """
        error_type, error_value, traceback = error_info = sys.exc_info()
        try:
            if ((not response.debug_mode) and
                (not self.is_loggable(error_value))):
                return

            try:
                short_message = u'{0}: {1}'.format(
                    error_type.__name__, error_value)
            except:
                short_message = error_type.__name__

            full_message = format_exception(error_type, error_value, traceback)
            for plugin in self.__subscribed:
                plugin(request, response, obj, error_info,
                       short_message, full_message, extra)
        finally:
            del traceback

    def get_last_errors(self):
        """Return all last errors.
        """
        errors = list(self.__last_errors)
        errors.reverse()
        return errors


reporter = ErrorReporter()


def log_last_error(request, response, obj=None, extra=None):
    """Log the last triggered error.
    """
    reporter.log_last_error(request, response, obj=obj, extra=extra)
