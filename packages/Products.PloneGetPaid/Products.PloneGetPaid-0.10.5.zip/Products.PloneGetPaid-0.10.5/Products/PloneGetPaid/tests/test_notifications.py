"""Integration test for notification sending
"""

import unittest
from Testing.ZopeTestCase import ZopeDocTestSuite
from utils import optionflags

from base import PloneGetPaidTestCase

class TestNotification(PloneGetPaidTestCase):

    def sendNotification():
        """
        First some mockup:

        >>> from zope import component, interface

        >>> from Products.PloneGetPaid import interfaces
        >>> from Products.PloneGetPaid import notifications

        >>> membership = self.portal.portal_membership
        >>> membership.addMember('testmanager', 'secret',
        ...                     ['Member', 'Manager'], [])

        >>> component.provideAdapter( notifications.CustomerOrderNotificationMessage,
        ...                          (interface.Interface, ),
        ...                           interfaces.INotificationMailMessage,
        ...                          'customer-new-order')
        >>> component.provideAdapter( notifications.MerchantOrderNotificationMessage,
        ...                          (interface.Interface, ),
        ...                           interfaces.INotificationMailMessage,
        ...                          'merchant-new-order')

        >>> component.provideAdapter( notifications.CustomerOrderNotificationMessage,
        ...                          (interface.Interface, ),
        ...                           interfaces.INotificationMailMessage,
        ...                          'customer-charge-order')
        >>> component.provideAdapter( notifications.MerchantOrderNotificationMessage,
        ...                          (interface.Interface, ),
        ...                           interfaces.INotificationMailMessage,
        ...                          'merchant-charge-order')

        >>> component.provideAdapter( notifications.CustomerOrderNotificationMessage,
        ...                          (interface.Interface, ),
        ...                           interfaces.INotificationMailMessage,
        ...                          'customer-decline-order')
        >>> component.provideAdapter( notifications.MerchantOrderNotificationMessage,
        ...                          (interface.Interface, ),
        ...                           interfaces.INotificationMailMessage,
        ...                          'merchant-decline-order')

        >>> settings = interfaces.IGetPaidManagementOptions( self.portal)
        >>> settings.send_merchant_auth_notification = True
        >>> settings.send_merchant_charge_notification = True
        >>> settings.send_merchant_decline_notification = True

        >>> settings.send_customer_auth_notification = True
        >>> settings.send_customer_charge_notification = True
        >>> settings.send_customer_decline_notification = True
        >>> settings.contact_email = 'merchant@foo.bar'

        >>> from zope import interface
        >>> class Mock(object):
        ...     interface.implements(interface.Interface)
        ...     def __init__(self, *args, **kwargs):
        ...         for k, v in kwargs.items(): setattr(self, k, v)

        >>> from getpaid.core.interfaces import workflow_states
        >>> finance = workflow_states.order.finance
        >>> eventAuth1 = Mock( source=finance.REVIEWING,
        ...                    destination=finance.CHARGEABLE,
        ...                    object=self.portal
        ...                  )

        >>> eventAuth2 = Mock( source=finance.PAYMENT_DECLINED,
        ...                    destination=finance.CHARGEABLE,
        ...                    object=self.portal
        ...                  )

        >>> eventCharged = Mock( source=finance.CHARGING,
        ...                      destination=finance.CHARGED,
        ...                      object=self.portal
        ...                    )

        >>> eventDeclined1 = Mock( source=finance.CHARGING,
        ...                        destination=finance.PAYMENT_DECLINED,
        ...                        object=self.portal
        ...                       )

        >>> eventDeclined2 = Mock( source=finance.REVIEWING,
        ...                        destination=finance.PAYMENT_DECLINED,
        ...                        object=self.portal
        ...                       )

        Extensions/install.py takes already care, that there is a LocalSite.
        However, setHooks still needs to be called - normally done by Five.

        >>> from zope.component.hooks import setHooks
        >>> setHooks()

        Call sendNotification with the mockups

        >>> from getpaid.core.tests.base import createOrders
        >>> from Products.PloneGetPaid.notifications import sendNotification
        >>> from Products.PloneGetPaid.member import ContactInfo
        >>> order = createOrders(how_many=2).next()
        >>> order.user_id = 'testmanager'
        >>> order.contact_information = ContactInfo()
        >>> order.contact_information.email = "example@example.com"
        >>> sendNotification( order, eventAuth1)
        >>> sendNotification( order, eventAuth2)
        >>> sendNotification( order, eventCharged)
        >>> sendNotification( order, eventDeclined1)
        >>> sendNotification( order, eventDeclined2)

        Now we overwrite the send method to raise an exception

        >>> def send_failing( self, msg):
        ...     raise Exception("This should be printed as an error message.")
        >>> self.portal.MailHost.send = send_failing

        And try again

        >>> sendNotification( order, eventAuth1)
        """

def test_suite():
    return unittest.TestSuite((
            ZopeDocTestSuite(test_class=TestNotification,
                             optionflags=optionflags),
        ))
