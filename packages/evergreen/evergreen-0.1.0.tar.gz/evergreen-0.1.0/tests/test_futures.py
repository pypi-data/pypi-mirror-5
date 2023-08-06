
from common import dummy, unittest, EvergreenTestCase

import os
import sys

import evergreen
from evergreen import futures


def dummy():
    return 42


class FuturesTests(EvergreenTestCase):

    def test_taskpool_executor(self):
        executor = futures.TaskPoolExecutor(10)
        def func():
            return 42
        def waiter():
            f = executor.submit(func)
            self.assertEqual(f.get(), 42)
        evergreen.spawn(waiter)
        self.loop.run()

    def test_taskpool_executor_raises(self):
        executor = futures.TaskPoolExecutor(10)
        def func():
            1/0
        def waiter():
            f = executor.submit(func)
            self.assertRaises(ZeroDivisionError, f.get)
        evergreen.spawn(waiter)
        self.loop.run()

    def test_threadpool_executor(self):
        executor = futures.ThreadPoolExecutor(5)
        def func():
            import time
            time.sleep(0.01)
            return 42
        def waiter():
            f = executor.submit(func)
            self.assertEqual(f.get(), 42)
        evergreen.spawn(waiter)
        self.loop.run()

    def test_processpool_executor(self):
        if 'TRAVIS' in os.environ:
            self.skipTest('Disabled on Travis')
            return
        if sys.platform == 'win32':
            self.skipTest('Temporarily disabled on Windows')
            return
        executor = futures.ProcessPoolExecutor(5)
        def waiter():
            f = executor.submit(dummy)
            self.assertEqual(f.get(), 42)
        evergreen.spawn(waiter)
        self.loop.run()

    def test_executor_with(self):
        def func():
            return 42
        def waiter():
            with futures.TaskPoolExecutor(5) as e:
                f = e.submit(func)
                self.assertEqual(f.get(), 42)
        evergreen.spawn(waiter)
        self.loop.run()

    def test_future_wait(self):
        executor = futures.TaskPoolExecutor(10)
        def func():
            evergreen.sleep(0.001)
            return 42
        def waiter():
            f = executor.submit(func)
            done, not_done = futures.wait([f])
            self.assertTrue(f in done)
            self.assertEqual(f.get(), 42)
        evergreen.spawn(waiter)
        self.loop.run()

    def test_future_wait_multiple(self):
        executor = futures.TaskPoolExecutor(10)
        def func():
            evergreen.sleep(0.001)
            return 42
        def waiter():
            f1 = executor.submit(func)
            f2 = executor.submit(func)
            done, not_done = futures.wait([f1, f2])
            self.assertTrue(f1 in done and f2 in done)
            self.assertEqual(f1.get(), 42)
            self.assertEqual(f2.get(), 42)
        evergreen.spawn(waiter)
        self.loop.run()

    def test_future_wait_multiple_wait_first(self):
        executor = futures.TaskPoolExecutor(10)
        def func(x):
            evergreen.sleep(x)
            return 42
        def waiter():
            f = executor.submit(func, 0.01)
            l = [f]
            for x in range(100):
                l.append(executor.submit(func, 100))
            done, not_done = futures.wait(l, return_when=futures.FIRST_COMPLETED)
            self.assertTrue(f in done)
            self.assertEqual(len(not_done), 100)
            self.assertEqual(f.get(), 42)
            self.loop.stop()
        evergreen.spawn(waiter)
        self.loop.run()

    def test_future_wait_multiple_exception(self):
        executor = futures.TaskPoolExecutor(10)
        def func():
            evergreen.sleep(0.001)
            return 42
        def raiser():
            1/0
        def waiter():
            f1 = executor.submit(raiser)
            f2 = executor.submit(func)
            f3 = executor.submit(func)
            done, not_done = futures.wait([f1, f2, f3], return_when=futures.FIRST_EXCEPTION)
            self.assertTrue(f1 in done)
            self.assertTrue(f2 in not_done and f3 in not_done)
            self.assertRaises(ZeroDivisionError, f1.get)
            self.loop.stop()
        evergreen.spawn(waiter)
        self.loop.run()

    def test_future_as_completed(self):
        executor = futures.TaskPoolExecutor(10)
        def func(x):
            evergreen.sleep(x)
            return 42
        def waiter():
            l = [executor.submit(func, 0.001) for x in range(10)]
            for f in futures.as_completed(l):
                self.assertEqual(f.get(), 42)
        evergreen.spawn(waiter)
        self.loop.run()

    def test_map(self):
        executor = futures.TaskPoolExecutor(10)
        def func(x):
            return x*x
        def waiter():
            l1 = [2, 4, 6]
            l2 = [4, 16, 36]
            r = list(executor.map(func, l1))
            self.assertEqual(r, l2)
        evergreen.spawn(waiter)
        self.loop.run()

    def test_reuse(self):
        f = futures.Future()
        f.set_result(42)
        self.assertEqual(f.get(), 42)
        self.assertRaises(RuntimeError, f.get)


if __name__ == '__main__':
    unittest.main(verbosity=2)

