# MIT License
# 
# Copyright (c) 2020 Alex Shafer
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from functools import wraps
from warnings import warn


class AmbisyncAlreadyCalled(Exception):
    pass


class AmbisyncMethodNotCalledWarning(Warning):
    pass


class Mode(object):
    pass


class _Sync(Mode):
    def __repr__(self):
        return 'SYNC'


class _Async(Mode):
    def __repr__(self):
        return 'ASYNC'


SYNC = _Sync()
ASYNC = _Async()


class args(object):
    def __init__(self, *args, **kwds):
        self.args = args
        self.kwds = kwds

    def call_with(self, func):
        return func(*self.args, **self.kwds)


def _call_with_args(func, args_obj):
    if isinstance(args_obj, args):
        return args_obj.call_with(func)
    else:
        return func()


class AmbisyncMethodCall(object):
    def __init__(self, name, mode, plan_spec, warn_not_called):
        self.name = name
        self.mode = mode
        self.plan_spec = plan_spec
        self._called = False
        self._warn_not_called_on_del = warn_not_called

    def __del__(self):
        if self._warn_not_called_on_del and not self._called:
            warn(f'Ambisync method not called ({self.name})', AmbisyncMethodNotCalledWarning)

    def _check_called(self):
        if self._called:
            raise AmbisyncAlreadyCalled()

    def do_sync_call(self):
        self._check_called()
        try:
            ret = None
            for subroutine_spec in self.plan_spec:
                ret = _call_with_args(subroutine_spec[0], ret)
            return ret
        finally:
            self._called = True

    async def do_async_call(self):
        self._check_called()
        try:
            ret = None
            for subroutine_spec in self.plan_spec:
                try:
                    subroutine = subroutine_spec[1]
                    sync = False
                except IndexError:
                    subroutine = subroutine_spec[0]
                    sync = True
                if sync:
                    ret = _call_with_args(subroutine, ret)
                else:
                    ret = await _call_with_args(subroutine, ret)
            return ret
        finally:
            self._called = True

    def do_call(self):
        if self.mode is SYNC:
            return self.do_sync_call()
        elif self.mode is ASYNC:
            return self.do_async_call()
        else:
            self._called = True
            raise RuntimeError('Unknown mode')


class AmbisyncClass(object):
    def __init__(self, mode):
        self._ambisync_mode = mode
        self._ambisync_warn_not_called_on_del = True

    def _ambisync(self, *plan_spec, name=None):
        return AmbisyncMethodCall(name,
                                  self._ambisync_mode,
                                  plan_spec,
                                  self._ambisync_warn_not_called_on_del)


def ambisync(method):
    @wraps(method)
    def wrapper(self, *args, **kwds):
        return method(self, *args, **kwds).do_call()
    return wrapper
