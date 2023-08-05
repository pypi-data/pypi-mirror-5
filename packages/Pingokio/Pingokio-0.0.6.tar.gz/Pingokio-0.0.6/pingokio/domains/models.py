#-*- coding:utf-8 -*-
import logging

from django.db import models

logger = logging.getLogger(__name__)


class Domain(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        verbose_name = u'domain'
        verbose_name_plural = 'domains'

    def __unicode__(self):
        return self.name


class AvailabilityTestCase(models.Model):
    POST = 'PO'
    GET = 'GE'
    PING = 'PI'
    TEST_CASE_KIND_CHOICES = (
        (POST, 'POST'),
        (GET, 'GET'),
        (PING, 'PING')
    )
    domain = models.ForeignKey(Domain)
    kind = models.CharField(max_length=2, choices=TEST_CASE_KIND_CHOICES, default=GET)
    url = models.URLField(max_length=500)
    parameters = models.TextField(max_length=600, null=True, blank=True)
    period = models.IntegerField(u'Interval in seconds', default=15)

    def __unicode__(self):
        return '{0} {1}'.format(self.domain, self.kind)


class CheckLog(models.Model):
    atc = models.ForeignKey(AvailabilityTestCase)
    result = models.TextField(max_length=1000, null=True, blank=True)
    status = models.BooleanField(null=False, blank=False, default=True)
    created = models.DateTimeField(auto_now_add=True)
