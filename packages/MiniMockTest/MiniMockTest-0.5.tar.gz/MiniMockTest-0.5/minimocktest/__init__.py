# (c) 2011 Hatem Nassrat 
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
'''
MiniMockTest module, holds MockTestCase class for easy to use mocking in testcases
'''

import __builtin__
import inspect
from unittest import TestCase
import minimock

class MockTestCase(TestCase):
    '''
    A TestCase class that integrates minimock functionailty
    `self.tt` minimock tracker object
    `self.mock` calls minimock.mock using tracker=`self.tt`
    `self.assertSameTrace` calls minimock.assert_same_trace with `self.tt`
    '''

    def setUp(self):
        TestCase.setUp(self)
        self.tt = minimock.TraceTracker()

    def tearDown(self):
        self.mockRestore()
        TestCase.tearDown(self)

    def Mock(self, *args, **kwargs):
        if 'tracker' not in kwargs:
            kwargs['tracker'] = self.tt
        return minimock.Mock(*args, **kwargs)

    def mock(self, *args, **kwargs):
        if len(args) <= 1 and 'nsdicts' not in kwargs:
            # custom nsdicts not used, inspect caller's stack
            stack = inspect.stack()
            try:
                # stack[1][0] is the frame object of the caller to this function
                globals_ = stack[1][0].f_globals
                locals_ = stack[1][0].f_locals
                nsdicts = (locals_, globals_, __builtin__.__dict__)
            finally:
                del(stack)
            kwargs['nsdicts'] = nsdicts
        if 'tracker' not in kwargs:
            kwargs['tracker'] = self.tt
        return minimock.mock(*args, **kwargs)

    def mockRestore(self):
        minimock.restore()

    def assertSameTrace(self, want):
        '''
        Asserts if want == trace
        '''
        minimock.assert_same_trace(self.tt, want)

    def assertTrace(self, want, includes=True):
        '''
        Asserts if want is included in trace, or excluded when includes=False
        '''
        trace = self.tt.dump()
        condition = want in trace
        fragment = 'not in'
        if not includes:
            condition = not condition
            fragment = 'in'
        self.assertTrue(condition, '%s %s trace:\n%s' %(want, fragment, trace))
