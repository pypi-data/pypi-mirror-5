#
#  subunit: extensions to python unittest to get test results from subprocesses.
#  Copyright (C) 2011  Robert Collins <robertc@robertcollins.net>
#
#  Licensed under either the Apache License, Version 2.0 or the BSD 3-clause
#  license at the users choice. A copy of both licenses are available in the
#  project source as Apache-2.0 and BSD. You may not use this file except in
#  compliance with one of these two licences.
#  
#  Unless required by applicable law or agreed to in writing, software
#  distributed under these licenses is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the
#  license you chose for the specific language governing permissions and
#  limitations under that license.
#

from testtools.compat import BytesIO
import unittest

from testtools import PlaceHolder
from testtools.testresult.doubles import StreamResult

import subunit
from subunit.run import SubunitTestRunner


def test_suite():
    loader = subunit.tests.TestUtil.TestLoader()
    result = loader.loadTestsFromName(__name__)
    return result


class TestSubunitTestRunner(unittest.TestCase):

    def test_includes_timing_output(self):
        io = BytesIO()
        runner = SubunitTestRunner(stream=io)
        test = PlaceHolder('name')
        runner.run(test)
        io.seek(0)
        eventstream = StreamResult()
        subunit.ByteStreamToStreamResult(io).run(eventstream)
        timestamps = [event[-1] for event in eventstream._events
            if event is not None]
        self.assertNotEqual([], timestamps)

    def test_enumerates_tests_before_run(self):
        io = BytesIO()
        runner = SubunitTestRunner(stream=io)
        test1 = PlaceHolder('name1')
        test2 = PlaceHolder('name2')
        case = unittest.TestSuite([test1, test2])
        runner.run(case)
        io.seek(0)
        eventstream = StreamResult()
        subunit.ByteStreamToStreamResult(io).run(eventstream)
        self.assertEqual([
            ('status', 'name1', 'exists'),
            ('status', 'name2', 'exists'),
            ], [event[:3] for event in eventstream._events[:2]])
