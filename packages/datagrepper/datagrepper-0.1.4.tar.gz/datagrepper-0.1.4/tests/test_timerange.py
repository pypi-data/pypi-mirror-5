import unittest
import datetime
import time

from nose.tools import eq_
from freezegun import freeze_time

from datagrepper.util import assemble_timerange


class TestTimerange(unittest.TestCase):

    @freeze_time('2012-01-01')
    def test_none_none_none(self):
        start, end, delta = assemble_timerange(None, None, None)
        eq_(None, start)
        eq_(None, end)
        eq_(None, delta)

    @freeze_time('2012-01-01')
    def test_delta_none_none(self):
        start, end, delta = assemble_timerange(None, None, 5)
        eq_(1325393995.0, start)
        eq_(1325394000.0, end)
        eq_(5, delta)

    @freeze_time('2012-01-01')
    def test_none_start_none(self):
        start = datetime.datetime.now() - datetime.timedelta(seconds=700)
        start = time.mktime(start.timetuple())
        start, end, delta = assemble_timerange(start, None, None)
        eq_(1325393300.0, start)
        eq_(1325394000.0, end)
        eq_(700, delta)

    @freeze_time('2012-01-01')
    def test_delta_start_none(self):
        start = datetime.datetime.now() - datetime.timedelta(seconds=600)
        start = time.mktime(start.timetuple())
        start, end, delta = assemble_timerange(start, None, 5)
        eq_(1325393400.0, start)
        eq_(1325393405.0, end)
        eq_(5, delta)

    @freeze_time('2012-01-01')
    def test_none_none_end(self):
        end = datetime.datetime.now() - datetime.timedelta(seconds=600)
        end = time.mktime(end.timetuple())
        start, end, delta = assemble_timerange(None, end, None)
        eq_(1325392800.0, start)
        eq_(1325393400.0, end)
        eq_(600, delta)

    @freeze_time('2012-01-01')
    def test_delta_none_end(self):
        end = datetime.datetime.now() - datetime.timedelta(seconds=600)
        end = time.mktime(end.timetuple())
        start, end, delta = assemble_timerange(None, end, 5)
        eq_(1325393395.0, start)
        eq_(1325393400.0, end)
        eq_(5, delta)

    @freeze_time('2012-01-01')
    def test_none_start_end(self):
        end = datetime.datetime.now() - datetime.timedelta(seconds=600)
        end = time.mktime(end.timetuple())
        start = datetime.datetime.now() - datetime.timedelta(seconds=800)
        start = time.mktime(start.timetuple())
        start, end, delta = assemble_timerange(start, end, None)
        eq_(1325393200.0, start)
        eq_(1325393400.0, end)
        eq_(200, delta)

    @freeze_time('2012-01-01')
    def test_delta_start_end(self):
        end = datetime.datetime.now() - datetime.timedelta(seconds=600)
        end = time.mktime(end.timetuple())
        start = datetime.datetime.now() - datetime.timedelta(seconds=800)
        start = time.mktime(start.timetuple())
        start, end, delta = assemble_timerange(start, end, 5)
        eq_(1325393200.0, start)
        eq_(1325393400.0, end)
        eq_(200, delta)
