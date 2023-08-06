"""
base

"""
import logging
import socket

LOGGER = logging.getLogger(__name__)


class Plugin(object):

    GUID = 'com.meetme.newrelic_plugin_agent'
    MAX_VAL = 2147483647

    def __init__(self, config, poll_interval, last_interval_values=None):
        self.poll_interval = poll_interval
        self.config = config

        self.derive_values = dict()
        self.derive_last_interval = last_interval_values or dict()


        self.derive_last_interval = last_interval_values or dict()
        self.gauge_values = dict()
        self.rate_values = dict()

    def add_derive_value(self, metric_name, units, value, count=None):
        """Add a value that will derive the current value from the difference
        between the last interval value and the current value.

        If this is the first time a stat is being added, it will report a 0
        value until the next poll interval and it is able to calculate the
        derivative value.

        :param str metric_name: The name of the metric
        :param str units: The unit type
        :param int value: The value to add
        :param int count: The number of items the timing is for

        """
        if value is None:
            value = 0
        metric = self.metric_name(metric_name, units)
        if metric not in self.derive_last_interval.keys():
            LOGGER.debug('Bypassing initial %s value for first run', metric)
            self.derive_values[metric] = self.metric_payload(0, count=0)
        else:
            cval = value - self.derive_last_interval[metric]
            self.derive_values[metric] = self.metric_payload(cval, count=count)
            LOGGER.debug('%s: Last: %r, Current: %r, Reporting: %r',
                         metric, self.derive_last_interval[metric], value,
                         self.derive_values[metric])
        self.derive_last_interval[metric] = value

    def add_derive_timing_value(self, metric_name, units, count, total_value,
                                last_value=None):
        """For timing based metrics that have a count of objects for the timing
        and an optional last value.

        :param str metric_name: The name of the metric
        :param str units: The unit type
        :param int count: The number of items the timing is for
        :param int total_value: The timing value
        :param int last_value: The last value

        """
        if last_value is None:
            return self.add_derive_value(metric_name, units, total_value, count)
        self.add_derive_value('%s/Total' % metric_name,
                              units, total_value, count)
        self.add_derive_value('%s/Last' % metric_name,
                              units, last_value, count)

    def add_gauge_value(self, metric_name, units, value,
                        min_val=None, max_val=None, count=None,
                        sum_of_squares=None):
        """Add a value that is not a rolling counter but rather an absolute
        gauge

        :param str metric_name: The name of the metric
        :param str units: The unit type
        :param int value: The value to add
        :param float value: The sum of squares for the values

        """
        metric = self.metric_name(metric_name, units)
        self.gauge_values[metric] = self.metric_payload(value,
                                                        min_val,
                                                        max_val,
                                                        count,
                                                        sum_of_squares)
        LOGGER.debug('%s: %r', metric_name, self.gauge_values[metric])

    def component_data(self):
        """Create the component section of the NewRelic Platform data payload
        message.

        :rtype: dict

        """
        metrics = dict()
        metrics.update(self.derive_values.items())
        metrics.update(self.gauge_values.items())
        metrics.update(self.rate_values.items())
        return {'name': self.name,
                'guid': self.GUID,
                'duration': self.poll_interval,
                'metrics': metrics}

    def initialize_counters(self, keys):
        """Create a new set of counters for the given key list

        :param list keys: Keys to initialize in the counters
        :rtype: tuple

        """
        count, total, min_val, max_val, values = (dict(), dict(), dict(),
                                                  dict(), dict())
        for key in keys:
            (count[key], total[key], min_val[key],
             max_val[key], values[key]) = 0, 0, self.MAX_VAL, 0, list()
        return count, total, min_val, max_val, values

    def metric_name(self, metric, units):
        """Return the metric name in the format for the NewRelic platform

        :param str metric: The name of th metric
        :param str units: The unit name

        """
        if not units:
            return 'Component/%s' % metric
        return 'Component/%s[%s]' % (metric, units)

    def metric_payload(self, value, min_value=None, max_value=None, count=None,
                       squares=None):
        """Return the metric in the standard payload format for the NewRelic
        agent.

        :rtype: dict

        """
        if isinstance(value, basestring):
            value = 0

        sum_of_squares = int(squares or (value * value))
        if sum_of_squares > self.MAX_VAL:
            sum_of_squares = 0

        return {'min': min_value,
                'max': max_value,
                'total': value,
                'count': count or 1,
                'sum_of_squares': sum_of_squares}

    @property
    def name(self):
        """Return the name of the component

        :rtype: str

        """
        return self.config.get('name', socket.gethostname().split('.')[0])

    def poll(self):
        """Poll the server returning the results in the expected component
        format.

        """
        raise NotImplementedError

    def sum_of_squares(self, values):
        """Return the sum_of_squares for the given values

        :param list values: The values list
        :rtype: float

        """
        value_sum = sum(values)
        if not value_sum:
            return 0
        squares = list()
        for value in values:
            squares.append(value * value)
        return sum(squares) - float(value_sum * value_sum) / len(values)

    def values(self):
        """Return the poll results

        :rtype: dict

        """
        return self.component_data()
