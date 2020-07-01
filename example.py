import asyncio
import time
from timeit import timeit

from ambisync import ambisync


class SomeClass(ambisync.BaseClass):
    """This is a very simple example AmbisyncClass

    For the example, the mode is explicitly passed in.
    I anticipate most users will determine the mode from
    some other parameter or config, and pass the desired
    constant to the constructor.
    """
    def __init__(self, myvar, mode):
        """Example user constructor"""

        # must explicitly call the ambisync.BaseClass constructor
        ambisync.BaseClass.__init__(self, mode)

        # example normal constructor
        self.myvar = myvar

    # The example ambisync method.
    # Must return self._ambisync(...)
    # Decorator is optional but recommended for semantic clarity

    @ambisync
    def my_method(self, myarg):
        """Test ambisync method"""

        # The function body must be broken up
        # into subroutines. They will only ever be
        # called in one sequence with no branching.

        # The first subroutine will not be passed any
        # arguments, but all subroutines can access
        # the method's namespace and arguments.

        # Return an args() to pass data into the
        # next subroutine as arguments. A return value
        # of any other type will be ignored, except
        # for the last subroutine in sequence,
        # see below.

        def sub1():
            print(f'subroutine 1 ({self.myvar})')
            return ambisync.args(5)

        # The second subroutine contains blocking
        # calls or an await. Two functionally
        # equivalent subroutines must be defined:
        # One synchronous and wrapping the blocking
        # call, and the other an async coroutine
        # wrapping the await.
        # Both must have the same argument signature
        # and return type(s).

        def sync_sub2(a):
            print(f'sync subroutine 2 starting ({self.myvar}) ({myarg})')
            time.sleep(3)
            print(f'sync subroutine 2 finished ({self.myvar}) ({a})')
            return ambisync.args(a+6, 'foo subarg')

        async def async_sub2(a):
            print(f'async subroutine 2 starting ({self.myvar}) ({myarg})')
            await asyncio.sleep(3)
            print(f'async subroutine 2 finished ({self.myvar}) ({a})')
            return ambisync.args(a+3, 'bar subarg')

        # A final example subroutine. 

        def sub3(a, b):
            print(f'subroutine 3 ({self.myvar}) ({a}, {b})')

            # The return of the final subroutine will be
            # returned from the method.
            # If any other subroutine returns a
            # non-args, it will be ignored
            return 'my_method done'

        # Arguments to _ambisync() define the subroutine
        # call sequence. They must be 1- or 2- tuples.
        # The first element must always be a synchronous
        # subroutine. The optional second element must
        # be an async sub-coroutine if present. 

        return self._ambisync(
            (sub1,),
            (sync_sub2, async_sub2),
            (sub3,),
        )


def main_synctest():
    """Example using SomeClass.my_method in sync mode"""
    def foo():
        time.sleep(1.3)
        print('foo')
    foo()
    sync_test = SomeClass('synctest', ambisync.SYNC)
    sync_test.my_method('foosync')


def main_asynctest():
    """Example using SomeClass.my_method in async mode"""
    async def testmain():
        async def foo():
            await asyncio.sleep(1.3)
            print('foo')
        asyncio.create_task(foo())
        sync_test_2 = SomeClass('asynctest2', ambisync.ASYNC)
        await sync_test_2.my_method('test2 async')

    asyncio.run(testmain())


class NoAmbiAsync(object):
    """This is an async-only version of SomeClass"""

    def __init__(self, myvar):
        self.myvar = myvar

    async def my_method(self, myarg):
        print(f'subroutine 1 ({self.myvar})')
        a = 5

        print(f'async subroutine 2 starting ({self.myvar}) ({myarg})')
        await asyncio.sleep(3)
        print(f'async subroutine 2 finished ({self.myvar}) ({a})')
        a = a+3
        b = 'bar subarg'

        print(f'subroutine 3 ({self.myvar}) ({a}, {b})')


def main_async_without_ambi():
    """Equivalent example without ambisync"""

    async def testmain():
        async def foo():
            await asyncio.sleep(1.3)
            print('foo')
        asyncio.create_task(foo())
        test = NoAmbiAsync('noambi test')
        await test.my_method('noambi arg')

    asyncio.run(testmain())


if __name__ == '__main__':
    tests = (
        (main_synctest, 4.3),
        (main_asynctest, 3),
        (main_async_without_ambi, 3),
    )

    n = 3
    for f, sec in tests:
        print(f'=== {f.__name__} ===')
        actual = timeit(f, number=n)/n
        print()
        print(f'Expected ~{sec} sec')
        print(f'Got {actual} sec')
        print()
