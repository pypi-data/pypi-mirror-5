# -*- coding: utf-8 -*-
"""
    jinja2.debug
    ~~~~~~~~~~~~

    Implements the debug interface for Jinja.  This module does some pretty
    ugly stuff with the Python traceback system in order to achieve tracebacks
    with correct line numbers, locals and contents.

    :copyright: (c) 2010 by the Jinja Team.
    :license: BSD, see LICENSE for more details.

    .. note::
        This file have been modified for Kivy usage, and its own kv language.
        We want to thanks a lot all the Jinja2 team for this awesome and ugly
        file ! :)
"""
import sys
import traceback
from types import TracebackType, CodeType

# on pypy we can take advantage of transparent proxies
try:
    import __pypy__ as tproxy
except ImportError:
    tproxy = None

internal_code = []


# how does the raise helper look like?
try:
    exec "raise TypeError, 'foo'"
except SyntaxError:
    raise_helper = 'raise __jinja_exception__[1]'
except TypeError:
    raise_helper = 'raise __jinja_exception__[0], __jinja_exception__[1]'


class TracebackFrameProxy(object):
    """Proxies a traceback frame."""

    def __init__(self, tb):
        self.tb = tb
        self._tb_next = None

    @property
    def tb_next(self):
        return self._tb_next

    def set_next(self, next):
        if tb_set_next is not None:
            try:
                tb_set_next(self.tb, next and next.tb or None)
            except Exception:
                # this function can fail due to all the hackery it does
                # on various python implementations.  We just catch errors
                # down and ignore them if necessary.
                pass
        self._tb_next = next

    def __getattr__(self, name):
        return getattr(self.tb, name)


def make_frame_proxy(frame):
    proxy = TracebackFrameProxy(frame)
    if tproxy is None:
        return proxy
    def operation_handler(operation, *args, **kwargs):
        if operation in ('__getattribute__', '__getattr__'):
            return getattr(proxy, args[0])
        elif operation == '__setattr__':
            proxy.__setattr__(*args, **kwargs)
        else:
            return getattr(proxy, operation)(*args, **kwargs)
    return tproxy(TracebackType, operation_handler)


class ProcessedTraceback(object):
    """Holds a Jinja preprocessed traceback for printing or reraising."""

    def __init__(self, exc_type, exc_value, frames):
        assert frames, 'no frames for this traceback?'
        self.exc_type = exc_type
        self.exc_value = exc_value
        self.frames = frames

        # newly concatenate the frames (which are proxies)
        prev_tb = None
        for tb in self.frames:
            if prev_tb is not None:
                prev_tb.set_next(tb)
            prev_tb = tb
        prev_tb.set_next(None)

    def render_as_text(self, limit=None):
        """Return a string with the traceback."""
        lines = traceback.format_exception(self.exc_type, self.exc_value,
                                           self.frames[0], limit=limit)
        return ''.join(lines).rstrip()

    @property
    def exc_info(self):
        """Exception info tuple with a proxy around the frame objects."""
        return self.exc_type, self.exc_value, self.frames[0]

    @property
    def standard_exc_info(self):
        """Standard python exc_info for re-raising"""
        tb = self.frames[0]
        # the frame will be an actual traceback (or transparent proxy) if
        # we are on pypy or a python implementation with support for tproxy
        if type(tb) is not TracebackType:
            tb = tb.tb
        return self.exc_type, self.exc_value, tb


def make_traceback(exc_info, source_hint=None):
    """Creates a processed traceback object from the exc_info."""
    exc_type, exc_value, tb = exc_info
    initial_skip = 1
    return translate_exception(exc_info, initial_skip)


def translate_syntax_error(error, source=None):
    """Rewrites a syntax error to please traceback systems."""
    error.source = source
    error.translated = True
    exc_info = (error.__class__, error, None)
    filename = error.filename
    if filename is None:
        filename = '<unknown>'
    return fake_exc_info(exc_info, filename, error.lineno)


def translate_exception(exc_info, initial_skip=0):
    """If passed an exc_info it will automatically rewrite the exceptions
    all the way down to the correct line numbers and frames.
    """
    tb = exc_info[2]
    frames = []

    # skip some internal frames if wanted
    for x in xrange(initial_skip):
        if tb is not None:
            tb = tb.tb_next

    while tb is not None:
        # skip frames decorated with @internalcode.  These are internal
        # calls we can't avoid and that are useless in template debugging
        # output.
        if tb.tb_frame.f_code in internal_code:
            tb = tb.tb_next
            continue

        # save a reference to the next frame if we override the current
        # one with a faked one.
        next = tb.tb_next

        # fake template exceptions
        kvlang = tb.tb_frame.f_locals.get('__kvlang__')
        if kvlang is not None:
            parser = kvlang.ctx
            line = kvlang.line + 1
            filename = parser.filename or '<string:%s>' % id(parser)
            tb = fake_exc_info(exc_info[:2] + (tb,), filename, line)[2]

        frames.append(make_frame_proxy(tb))
        tb = next

    # if we don't have any exceptions in the frames left, we have to
    # reraise it unchanged.
    # XXX: can we backup here?  when could this happen?
    if not frames:
        raise exc_info[0], exc_info[1], exc_info[2]

    return ProcessedTraceback(exc_info[0], exc_info[1], frames)


def fake_exc_info(exc_info, filename, lineno):
    """Helper for `translate_exception`."""
    exc_type, exc_value, tb = exc_info

    # figure the real context out
    if tb is not None:
        real_locals = tb.tb_frame.f_locals.copy()
        ctx = real_locals.get('context')
        if ctx:
            locals = ctx.get_all()
        else:
            locals = {}
        for name, value in real_locals.iteritems():
            if name.startswith('l_'):
                locals[name[2:]] = value

        # if there is a local called __jinja_exception__, we get
        # rid of it to not break the debug functionality.
        locals.pop('__jinja_exception__', None)
    else:
        locals = {}

    # assamble fake globals we need
    globals = {
        '__name__':             filename,
        '__file__':             filename,
        '__jinja_exception__':  exc_info[:2],

        # we don't want to keep the reference to the template around
        # to not cause circular dependencies, but we mark it as Jinja
        # frame for the ProcessedTraceback
        '__jinja_template__':   None
    }

    # and fake the exception
    code = compile('\n' * (lineno - 1) + raise_helper, filename, 'exec')

    # if it's possible, change the name of the code.  This won't work
    # on some python environments such as google appengine
    try:
        if tb is None:
            location = 'template'
        else:
            function = tb.tb_frame.f_code.co_name
            location = function
        code = CodeType(0, code.co_nlocals, code.co_stacksize,
                        code.co_flags, code.co_code, code.co_consts,
                        code.co_names, code.co_varnames, filename,
                        location, code.co_firstlineno,
                        code.co_lnotab, (), ())
    except:
        pass

    # execute the code and catch the new traceback
    try:
        exec code in globals, locals
    except:
        exc_info = sys.exc_info()
        new_tb = exc_info[2].tb_next

    # return without this frame
    return exc_info[:2] + (new_tb,)


def _init_ugly_crap():
    """This function implements a few ugly things so that we can patch the
    traceback objects.  The function returned allows resetting `tb_next` on
    any python traceback object.  Do not attempt to use this on non cpython
    interpreters
    """
    import ctypes
    from types import TracebackType

    # figure out side of _Py_ssize_t
    if hasattr(ctypes.pythonapi, 'Py_InitModule4_64'):
        _Py_ssize_t = ctypes.c_int64
    else:
        _Py_ssize_t = ctypes.c_int

    # regular python
    class _PyObject(ctypes.Structure):
        pass
    _PyObject._fields_ = [
        ('ob_refcnt', _Py_ssize_t),
        ('ob_type', ctypes.POINTER(_PyObject))
    ]

    # python with trace
    if hasattr(sys, 'getobjects'):
        class _PyObject(ctypes.Structure):
            pass
        _PyObject._fields_ = [
            ('_ob_next', ctypes.POINTER(_PyObject)),
            ('_ob_prev', ctypes.POINTER(_PyObject)),
            ('ob_refcnt', _Py_ssize_t),
            ('ob_type', ctypes.POINTER(_PyObject))
        ]

    class _Traceback(_PyObject):
        pass
    _Traceback._fields_ = [
        ('tb_next', ctypes.POINTER(_Traceback)),
        ('tb_frame', ctypes.POINTER(_PyObject)),
        ('tb_lasti', ctypes.c_int),
        ('tb_lineno', ctypes.c_int)
    ]

    def tb_set_next(tb, next):
        """Set the tb_next attribute of a traceback object."""
        if not (isinstance(tb, TracebackType) and
                (next is None or isinstance(next, TracebackType))):
            raise TypeError('tb_set_next arguments must be traceback objects')
        obj = _Traceback.from_address(id(tb))
        if tb.tb_next is not None:
            old = _Traceback.from_address(id(tb.tb_next))
            old.ob_refcnt -= 1
        if next is None:
            obj.tb_next = ctypes.POINTER(_Traceback)()
        else:
            next = _Traceback.from_address(id(next))
            next.ob_refcnt += 1
            obj.tb_next = ctypes.pointer(next)

    return tb_set_next


# try to get a tb_set_next implementation if we don't have transparent
# proxies.
tb_set_next = None
if tproxy is None:
    try:
        tb_set_next = _init_ugly_crap()
    except ImportError:
        tb_set_next = None
    del _init_ugly_crap
