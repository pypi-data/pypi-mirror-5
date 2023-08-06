# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import with_statement

import logging

from django.conf import settings
from django.core.signals import got_request_exception
from django.test import TestCase

from heka.tests.helpers import decode_message
from raven.contrib.django import DjangoClient
from raven.contrib.django.models import get_client

settings.SENTRY_CLIENT = 'tests.contrib.django.tests.TempStoreClient'
DSN='udp://1007818f46e44c2f9a03b684dcff87b4:6391e66ef7194b67bd41c23851c7b03a@192.168.20.2:9001/2'

TESTING_PROJECT_ID = 2
DSN = 'udp://1007818f46e44c2f9a03b684dcff87b4:6391e66ef7194b67bd41c23851c7b03a@192.168.20.2:9001/%d'
DSN = DSN % TESTING_PROJECT_ID

class TempStoreClient(DjangoClient):
    def __init__(self, *args, **kwargs):
        self.events = []
        super(TempStoreClient, self).__init__(*args, **kwargs)

    def send(self, **kwargs):
        self.events.append(kwargs)

    def is_enabled(self, **kwargs):
        return True


class Settings(object):
    """
    Allows you to define settings that are required for this function to work.

    >>> with Settings(SENTRY_LOGIN_URL='foo'): #doctest: +SKIP
    >>>     print settings.SENTRY_LOGIN_URL #doctest: +SKIP
    """

    NotDefined = object()

    def __init__(self, **overrides):
        self.overrides = overrides
        self._orig = {}

    def __enter__(self):
        for k, v in self.overrides.iteritems():
            self._orig[k] = getattr(settings, k, self.NotDefined)
            setattr(settings, k, v)

    def __exit__(self, exc_type, exc_value, traceback):
        for k, v in self._orig.iteritems():
            if v is self.NotDefined:
                delattr(settings, k)
            else:
                setattr(settings, k, v)


class DjangoHekaTransport(TestCase):
    ## Fixture setup/teardown
    urls = 'tests.contrib.django.urls'

    def setUp(self):
        """
        This is not entirely obvious.

        settings.SENTRY_CLIENT :
            * This is the classname of the object that
              raven.contrib.django.models.get_client() will return.

              The sentry client is a subclass of raven.base.Client.

              This is the control point that all messages are going
              to get routed through

              For heka integration, this *must* be
              'raven_heka.djangoheka.HekaDjangoClient'

        settings.HEKA_CONF :
            * configuration for the heka client instance

        settings.HEKA :
            * This is the actual heka client instance
        """

        self.HEKA_CONF = {
                'stream_class': 'heka.streams.DebugCaptureStream',
                'plugins': {'raven':
                    ('heka_raven.raven_plugin:config_plugin', {'dsn':
                        DSN})
                    },
        }

        self.SENTRY_CLIENT = 'djangoraven.heka.HekaDjangoClient'

        from heka.config import client_from_dict_config
        self.HEKA = client_from_dict_config(self.HEKA_CONF)

    def test_basic(self):
        with Settings(HEKA_CONF=self.HEKA_CONF,
                      HEKA=self.HEKA,
                      SENTRY_CLIENT=self.SENTRY_CLIENT,
                      SENTRY_DSN=DSN):

            self.raven = get_client()

            self.raven.capture('Message', message='foo')

            msgs = []
            for mdata in settings.HEKA.stream.msgs:
                h, m = decode_message(mdata)
                msgs.append(m)

            self.assertEquals(len(msgs), 1)
            event = self.raven.decode(msgs[0].payload)

            self.assertTrue('sentry.interfaces.Message' in event)
            message = event['sentry.interfaces.Message']
            self.assertEquals(message['message'], 'foo')
            self.assertEquals(event['level'], logging.ERROR)
            self.assertEquals(event['message'], 'foo')

            # The project_id must be extracted from the SENTRY_DSN
            # option
            self.assertEquals(event['project'],
                    str(TESTING_PROJECT_ID))

            # This is different than the regular Django test as we are
            # *decoding* a serialized message - so instead of checking
            # for datetime, we expect a string
            self.assertTrue(isinstance(event['timestamp'], basestring))

    def test_signal_integration(self):
        with Settings(HEKA_CONF=self.HEKA_CONF,
                      HEKA=self.HEKA,
                      SENTRY_CLIENT=self.SENTRY_CLIENT,
                      SENTRY_DSN=DSN):

            self.raven = get_client()

            try:
                int('hello')
            except:
                got_request_exception.send(sender=self.__class__, request=None)
            else:
                self.fail('Expected an exception.')

            msgs = []
            for mdata in settings.HEKA.stream.msgs:
                h, m = decode_message(mdata)
                msgs.append(m)

            self.assertEquals(len(msgs), 1)

            event = self.raven.decode(msgs[0].payload)
            self.assertTrue('sentry.interfaces.Exception' in event)
            exc = event['sentry.interfaces.Exception']
            self.assertEquals(exc['type'], 'ValueError')
            self.assertEquals(exc['value'], u"invalid literal for int() with base 10: 'hello'")
            self.assertEquals(event['level'], logging.ERROR)
            self.assertEquals(event['message'], u"ValueError: invalid literal for int() with base 10: 'hello'")
            self.assertEquals(event['culprit'],
                    'tests.contrib.django.tests in test_signal_integration')

            # The project_id must be extracted from the SENTRY_DSN
            # option
            self.assertEquals(event['project'],
                    str(TESTING_PROJECT_ID))
