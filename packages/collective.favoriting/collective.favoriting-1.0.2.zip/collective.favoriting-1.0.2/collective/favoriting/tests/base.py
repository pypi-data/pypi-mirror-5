import transaction
import unittest2 as unittest
from plone.app.testing import setRoles, TEST_USER_ID
from collective.favoriting import testing


class UnitTestCase(unittest.TestCase):

    def setUp(self):
        pass


class IntegrationTestCase(unittest.TestCase):

    layer = testing.INTEGRATION

    def setUp(self):
        super(IntegrationTestCase, self).setUp()
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.setRole("Manager")
        self.portal.invokeFactory('Document', 'test-document')
        self.setRole("Member")
        self.document = self.portal['test-document']

    def setRole(self, role="Member"):
        setRoles(self.portal, TEST_USER_ID, [role])


class FunctionalTestCase(IntegrationTestCase):

    layer = testing.FUNCTIONAL

    def setUp(self):
        #we must commit the transaction
        transaction.commit()
