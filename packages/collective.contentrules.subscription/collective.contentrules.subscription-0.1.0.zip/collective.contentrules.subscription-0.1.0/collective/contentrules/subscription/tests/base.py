# -*- coding: utf-8 -*-

import unittest
from zope import interface
from collective.contentrules.subscription.browser.interfaces import IContentrulesSubscriptionLayer


class BaseTestCase(unittest.TestCase):

    def markRequestWithLayer(self):
        # to be removed when p.a.testing will fix https://dev.plone.org/ticket/11673
        request = self.layer['request']
        interface.alsoProvides(request, IContentrulesSubscriptionLayer)
