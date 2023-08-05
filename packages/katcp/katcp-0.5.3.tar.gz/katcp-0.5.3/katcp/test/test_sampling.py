# test_sampling.py
# -*- coding: utf8 -*-
# vim:fileencoding=utf8 ai ts=4 sts=4 et sw=4
# Copyright 2009 SKA South Africa (http://ska.ac.za/)
# BSD license - see COPYING for details

"""Tests for the katcp.sampling module.
   """

import unittest
import time
import logging
import katcp
from katcp.testutils import TestLogHandler, DeviceTestSensor
from katcp import sampling, Sensor

log_handler = TestLogHandler()
logging.getLogger("katcp").addHandler(log_handler)


class TestSampling(unittest.TestCase):

    def setUp(self):
        """Set up for test."""
        # test sensor
        self.sensor = DeviceTestSensor(
                Sensor.INTEGER, "an.int", "An integer.", "count",
                [-4, 3],
                timestamp=12345, status=Sensor.NOMINAL, value=3)

        # test callback
        def inform(sensor_name, timestamp, status, value):
            self.calls.append(sampling.format_inform_v5(
                sensor_name, timestamp, status, value) )

        self.calls = []
        self.inform = inform

    def test_sampling(self):
        """Test getting and setting the sampling."""
        s = self.sensor

        sampling.SampleNone(None, s)
        sampling.SampleAuto(None, s)
        sampling.SamplePeriod(None, s, 10)
        sampling.SampleEvent(None, s)
        sampling.SampleDifferential(None, s, 2)
        self.assertRaises(ValueError, sampling.SampleNone, None, s, "foo")
        self.assertRaises(ValueError, sampling.SampleAuto, None, s, "bar")
        self.assertRaises(ValueError, sampling.SamplePeriod, None, s)
        self.assertRaises(ValueError, sampling.SamplePeriod, None, s, "0")
        self.assertRaises(ValueError, sampling.SamplePeriod, None, s, "-1")
        self.assertRaises(ValueError, sampling.SampleEvent, None, s, "foo")
        self.assertRaises(ValueError, sampling.SampleDifferential, None, s)
        self.assertRaises(ValueError, sampling.SampleDifferential,
                          None, s, "-1")
        self.assertRaises(ValueError, sampling.SampleDifferential,
                          None, s, "1.5")

        sampling.SampleStrategy.get_strategy("none", None, s)
        sampling.SampleStrategy.get_strategy("auto", None, s)
        sampling.SampleStrategy.get_strategy("period", None, s, "15")
        sampling.SampleStrategy.get_strategy("event", None, s)
        sampling.SampleStrategy.get_strategy("differential", None, s, "2")
        self.assertRaises(ValueError, sampling.SampleStrategy.get_strategy,
                          "random", None, s)
        self.assertRaises(ValueError, sampling.SampleStrategy.get_strategy,
                          "period", None, s, "foo")
        self.assertRaises(ValueError, sampling.SampleStrategy.get_strategy,
                          "differential", None, s, "bar")

    def test_event(self):
        """Test SampleEvent strategy."""
        event = sampling.SampleEvent(self.inform, self.sensor)
        self.assertEqual(event.get_sampling_formatted(),
                         ('event', []) )

        self.assertEqual(self.calls, [])

        event.attach()
        self.assertEqual(len(self.calls), 1)

        self.sensor.set_value(2, status=Sensor.NOMINAL)
        self.assertEqual(len(self.calls), 2)

        # Test that an update is suppressed if the sensor value is unchanged
        self.sensor.set_value(2, status=Sensor.NOMINAL)
        self.assertEqual(len(self.calls), 2)

        # Test that an update happens if the status changes even if the value is
        # unchanged
        self.sensor.set_value(2, status=Sensor.WARN)
        self.assertEqual(len(self.calls), 3)


    def test_differential(self):
        """Test SampleDifferential strategy."""
        diff = sampling.SampleDifferential(self.inform, self.sensor, 5)
        self.assertEqual(self.calls, [])

        diff.attach()
        self.assertEqual(len(self.calls), 1)

    def test_differential_timestamp(self):
        # Test that the timetamp differential is stored correctly as
        # seconds. This is mainly to check the conversion of the katcp spec from
        # milliseconds to seconds for katcp v5 spec.
        time_diff = 4.12                  # Time differential in seconds
        ts_sensor = Sensor(Sensor.TIMESTAMP, 'ts', 'ts sensor', '')
        diff = sampling.SampleDifferential(self.inform, ts_sensor, time_diff)
        self.assertEqual(diff._threshold, time_diff)

    def test_periodic(self):
        """Test SamplePeriod strategy."""
        sample_p = 10                            # sample period in seconds
        period = sampling.SamplePeriod(self.inform, self.sensor, sample_p)
        self.assertEqual(self.calls, [])

        period.attach()
        self.assertEqual(self.calls, [])

        next_p = period.periodic(1)
        self.assertEqual(next_p, 1 + sample_p)
        self.assertEqual(len(self.calls), 1)

        next_p = period.periodic(11)
        self.assertEqual(len(self.calls), 2)
        self.assertEqual(next_p, 11 + sample_p)

        next_p = period.periodic(12)
        self.assertEqual(next_p, 12 + sample_p)
        self.assertEqual(len(self.calls), 3)

    def test_event_rate(self):
        """Test SampleEventRate strategy."""
        shortest = 10
        longest = 20
        evrate = sampling.SampleEventRate(
            self.inform, self.sensor, shortest, longest)
        now = [1]
        evrate._time = lambda: now[0]
        self.assertEqual(self.calls, [])

        evrate.attach()
        self.assertEqual(len(self.calls), 1)

        self.sensor.set_value(1)
        self.assertEqual(len(self.calls), 1)

        now[0] = 11
        self.sensor.set_value(2)
        self.assertEqual(len(self.calls), 2)

        evrate.periodic(12)
        self.assertEqual(len(self.calls), 2)
        evrate.periodic(13)
        self.assertEqual(len(self.calls), 2)
        evrate.periodic(31)
        self.assertEqual(len(self.calls), 3)

        now[0] = 32
        self.sensor.set_value(3)
        self.assertEqual(len(self.calls), 3)

        now[0] = 41
        self.sensor.set_value(1)
        self.assertEqual(len(self.calls), 4)

    def test_event_rate_fractions(self):
        # Test SampleEventRate strategy in the presence of fractional seconds --
        # mainly to catch bugs when it was converted to taking seconds instead of
        # milliseconds, since the previous implementation used an integer number
        # of milliseconds
        shortest = 3./8
        longest = 6./8
        evrate = sampling.SampleEventRate(self.inform, self.sensor, shortest,
                                          longest)
        now = [0]
        evrate._time = lambda: now[0]

        evrate.attach()
        self.assertEqual(len(self.calls), 1)

        now[0] = 0.999*shortest
        self.sensor.set_value(1)
        self.assertEqual(len(self.calls), 1)

        now[0] = shortest
        self.sensor.set_value(1)
        self.assertEqual(len(self.calls), 2)

        next_time = evrate.periodic(now[0] + 0.99*shortest)
        self.assertEqual(len(self.calls), 2)
        self.assertEqual(next_time, now[0] + longest)

class TestReactor(unittest.TestCase):

    def setUp(self):
        """Set up for test."""
        # test sensor
        self.sensor = DeviceTestSensor(
                Sensor.INTEGER, "an.int", "An integer.", "count",
                [-4, 3],
                timestamp=12345, status=Sensor.NOMINAL, value=3)

        # test callback
        def inform(sensor_name, timestamp, status, value):
            self.calls.append(sampling.format_inform_v5(
                sensor_name, timestamp, status, value) )

        # test reactor
        self.reactor = sampling.SampleReactor()
        self.reactor.start()

        self.calls = []
        self.inform = inform

    def tearDown(self):
        """Clean up after test."""
        self.reactor.stop()
        self.reactor.join(1.0)

    def test_periodic(self):
        """Test reactor with periodic sampling."""
        period = sampling.SamplePeriod(self.inform, self.sensor, 10./1000)
        start = time.time()
        self.reactor.add_strategy(period)
        time.sleep(0.1)
        self.reactor.remove_strategy(period)
        end = time.time()

        expected = int(round((end - start) / 0.01))
        emax, emin = expected + 1, expected - 1

        self.assertTrue(emin <= len(self.calls) <= emax,
                        "Expect %d to %d informs, got:\n  %s" %
                        (emin, emax, "\n  ".join(str(x) for x in self.calls)))
