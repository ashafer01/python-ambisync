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


class AmbisyncError(Exception):
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
    """Anonymous function arguments"""

    def __init__(self, *args, **kwds):
        self.args = args
        self.kwds = kwds

    def call_with(self, func):
        """Call a function with our arguments"""
        return func(*self.args, **self.kwds)


def _call_with_args(func, args_obj):
    if isinstance(args_obj, args):
        return args_obj.call_with(func)
    else:
        return func()


def _do_sync_call(plan_spec):
    """Synchronously run a plan spec"""
    ret = None
    for subroutine_spec in plan_spec:
        try:
            subroutine = subroutine_spec[0]
        except TypeError:
            subroutine = subroutine_spec
        ret = _call_with_args(subroutine, ret)
    return ret


async def _do_async_call(plan_spec):
    """Asynchronously run a plan spec"""
    ret = None
    for subroutine_spec in plan_spec:
        sync = True
        try:
            subroutine = subroutine_spec[1]
            sync = False
        except IndexError:
            subroutine = subroutine_spec[0]
        except TypeError:
            subroutine = subroutine_spec
        if sync:
            ret = _call_with_args(subroutine, ret)
        else:
            ret = await _call_with_args(subroutine, ret)
    return ret


class AmbisyncBaseClass(object):
    """Base class/mixin for classes containing Ambisync methods"""

    def __init__(self, mode):
        if mode is not SYNC and mode is not ASYNC:
            raise AmbisyncError('mode must be ambisync.SYNC or ambisync.ASYNC')
        self._ambisync_mode = mode

    def _ambisync(self, *plan_spec):
        if self._ambisync_mode is SYNC:
            # run the plan before returning, and return the result
            return _do_sync_call(plan_spec)
        elif self._ambisync_mode is ASYNC:
            # create the coroutine object for the caller to await
            return _do_async_call(plan_spec)
        else:
            raise RuntimeError('Unknown _ambisync_mode')


class _Ambisync(object):
    """For use with `from ambisync import ambisync` when combined with below definitions"""

    # For ambisync.* to make sense
    BaseClass = AmbisyncBaseClass
    args = args
    SYNC = SYNC
    ASYNC = ASYNC

    # optional @ambisync decorator for a semantic indicator at the top of a method definition
    def __call__(self, method):
        return method


ambisync = _Ambisync()
__all__ = ['ambisync']
