#
# This file is part of Evergreen. See the NOTICE for more information.
#

import evergreen

__all__ = ['Timeout']


class Timeout(BaseException):
    """Raises *exception* in the current task after *timeout* seconds.

    When *exception* is omitted or ``None``, the :class:`Timeout` instance
    itself is raised. If *seconds* is None, the timer is not scheduled, and is
    only useful if you're planning to raise it directly.

    Timeout objects are context managers, and so can be used in with statements.
    When used in a with statement, if *exception* is ``False``, the timeout is
    still raised, but the context manager suppresses it, so the code outside the
    with-block won't see it.
    """

    def __init__(self, seconds=None, exception=None):
        self.seconds = seconds
        self.exception = exception
        self._timer = None

    def start(self):
        """Schedule the timeout.  This is called on construction, so
        it should not be called explicitly, unless the timer has been
        canceled."""
        assert not self._timer, '%r is already started; to restart it, cancel it first' % self
        loop = evergreen.current.loop
        current = evergreen.current.task
        if self.seconds is None or self.seconds < 0:
            # "fake" timeout (never expires)
            self._timer = None
        elif self.exception is None or isinstance(self.exception, bool):
            # timeout that raises self
            self._timer = loop.call_later(self.seconds, self._timer_cb, current.throw, self)
        else:
            # regular timeout with user-provided exception
            self._timer = loop.call_later(self.seconds, self._timer_cb, current.throw, self.exception)

    def _timer_cb(self, func, arg):
        self._timer = None
        func(arg)

    def cancel(self):
        """If the timeout is pending, cancel it.  If not using
        Timeouts in ``with`` statements, always call cancel() in a
        ``finally`` after the block of code that is getting timed out.
        If not canceled, the timeout will be raised later on, in some
        unexpected section of the application."""
        if self._timer is not None:
            self._timer.cancel()
            self._timer = None

    def __repr__(self):
        if self.exception is None:
            exception = ''
        else:
            exception = ' exception=%r' % self.exception
        return '<%s at %s seconds=%s%s>' % (
            self.__class__.__name__, hex(id(self)), self.seconds, exception)

    def __str__(self):
        if self.seconds is None:
            return ''
        if self.seconds == 1:
            suffix = ''
        else:
            suffix = 's'
        if self.exception is None or self.exception is True:
            return '%s second%s' % (self.seconds, suffix)
        elif self.exception is False:
            return '%s second%s (silent)' % (self.seconds, suffix)
        else:
            return '%s second%s (%s)' % (self.seconds, suffix, self.exception)

    def __enter__(self):
        if not self._timer:
            self.start()
        return self

    def __exit__(self, typ, value, tb):
        self.cancel()
        if value is self and self.exception is False:
            return True

