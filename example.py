import asyncio
import time
from timeit import timeit

from ambisync import ambisync, args, AmbisyncClass, SYNC, ASYNC


class SomeClass(AmbisyncClass):
    def __init__(self, myvar, mode):
        AmbisyncClass.__init__(self, mode)
        self.myvar = myvar

    @ambisync
    def my_method(self, myarg):
        """Test ambisync method"""
        def sub1():
            print(f'subroutine 1 ({self.myvar})')
            return args(5)

        def sync_sub2(a):
            print(f'sync subroutine 2 starting ({self.myvar}) ({myarg})')
            time.sleep(3)
            print(f'sync subroutine 2 finished ({self.myvar}) ({a})')
            return args(a+6, 'foo subarg')

        async def async_sub2(a):
            print(f'async subroutine 2 starting ({self.myvar}) ({myarg})')
            await asyncio.sleep(3)
            print(f'async subroutine 2 finished ({self.myvar}) ({a})')
            return args(a+3, 'bar subarg')

        def sub3(a, b):
            print(f'subroutine 3 ({self.myvar}) ({a}, {b})')

        return self._ambisync(
            (sub1,),
            (sync_sub2, async_sub2),
            (sub3,),
        )


def main_synctest():
    def foo():
        time.sleep(1.3)
        print('foo')
    foo()
    sync_test = SomeClass('synctest', SYNC)
    sync_test.my_method('foosync')


def main_asynctest():
    async def testmain():
        async def foo():
            await asyncio.sleep(1.3)
            print('foo')
        asyncio.create_task(foo())
        sync_test_2 = SomeClass('asynctest2', ASYNC)
        await sync_test_2.my_method('test2 async')

    asyncio.run(testmain())


class NoAmbiAsync(object):
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
