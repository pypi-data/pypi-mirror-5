# Copyright (c) 2013, The MITRE Corporation. All rights reserved.
# See LICENSE.txt for complete terms.

import datetime
import unittest

from cybox.common import String, DateTime
from cybox.objects.address_object import Address, EmailAddress
from cybox.objects.email_message_object import (AttachmentReference,
        Attachments, EmailHeader, EmailMessage, EmailRecipients, LinkReference,
        Links, ReceivedLine, ReceivedLineList)
import cybox.test
from cybox.test.objects import ObjectTestCase


class TestLinks(unittest.TestCase):

    def test_round_trip(self):
        linkref_dict = {'object_reference': "example:URI-C2"}
        linkref_dict2 = cybox.test.round_trip_dict(LinkReference, linkref_dict)
        self.assertEqual(linkref_dict, linkref_dict2)

    def test_round_trip_list(self):
        l = Links()
        l.append("example:URI-watchlist1")
        l.append("example:URI-watchlist2")
        l2 = cybox.test.round_trip(l, list_=True)
        self.assertEqual(l.to_list(), l2.to_list())


class TestAttachments(unittest.TestCase):

    def test_round_trip(self):
        attref_dict = {'object_reference': "abc-123"}
        attref_dict2 = cybox.test.round_trip_dict(AttachmentReference, attref_dict)
        self.assertEqual(attref_dict, attref_dict2)

    def test_round_trip_list(self):
        a = Attachments()
        a.append("example:File-A1")
        a.append("example:File-A3")
        a2 = cybox.test.round_trip(a, list_=True)
        self.assertEqual(a.to_list(), a2.to_list())


class TestReceivedLine(unittest.TestCase):

    def test_round_trip(self):
        rline_dict = {
                        'from': "sending.mail.server",
                        'by': "receiving.mail.server",
                        'with': "ESMTP",
                        'for': "recipient@example.com",
                        'id': "test.id@test.local",
                        'timestamp': "Mon, Apr 29 2013 13:00:00-0500"
                     }
        rline_dict2 = cybox.test.round_trip_dict(ReceivedLine, rline_dict)
        cybox.test.assert_equal_ignore(rline_dict, rline_dict2, ['timestamp'])
        self.assertEqual("2013-04-29T13:00:00-05:00", rline_dict2['timestamp'])


class TestReceivedLineList(unittest.TestCase):

    def test_round_trip(self):
        rline_list = [{'from': "a", 'by': "b", 'for': 'c'},
                      {'from': "d", 'by': "e", 'for': 'f'}]
        rline_list2 = cybox.test.round_trip_list(ReceivedLineList, rline_list)
        self.assertEqual(rline_list, rline_list2)


class TestEmailRecipients(unittest.TestCase):
    def setUp(self):
        self.email1 = "victim1@target.com"
        self.email2 = "victim2@target.com"

    # Five different ways to build an EmailRecipients list

    def test_list(self):
        recips = EmailRecipients(Address(self.email1, Address.CAT_EMAIL),
                                 Address(self.email2, Address.CAT_EMAIL))
        self._compare(recips)

    def test_list2(self):
        recips = EmailRecipients(EmailAddress(self.email1),
                                 EmailAddress(self.email2))
        self._compare(recips)

    def test_list3(self):
        recips = EmailRecipients(self.email1, self.email2)
        self._compare(recips)

    def test_list4(self):
        recips = EmailRecipients()
        recips.append(self.email1)
        recips.append(self.email2)
        self._compare(recips)

    def test_list5(self):
        recips = EmailRecipients()
        recips.append(EmailAddress(self.email1))
        recips.append(EmailAddress(self.email2))
        self._compare(recips)

    def _compare(self, recips):
        recips2 = cybox.test.round_trip(recips, list_=True)
        self.assertEqual(2, len(recips2))

        recips_list = recips2.to_list()
        self.assertEqual(recips_list[0]['category'], Address.CAT_EMAIL)
        self.assertEqual(recips_list[0]['address_value'], self.email1)
        self.assertEqual(recips_list[1]['category'], Address.CAT_EMAIL)
        self.assertEqual(recips_list[1]['address_value'], self.email2)

    def test_invalid_recip_type(self):
        ipv4 = Address("1.2.3.4", Address.CAT_IPV4)
        for a in [dict(a=1), 1, True, [1], ipv4]:
            self.assertRaises(ValueError, EmailRecipients, a)


class TestEmailHeader(unittest.TestCase):

    def setUp(self):
        self.datetime_str = "2010-12-10T14:15:30+02:00"

    def test_roundtrip(self):
        d = {
                'received_lines': [{'from': "a", 'by': "b"}],
                'to': [{'address_value': "victim@example.com",
                        'category': Address.CAT_EMAIL,
                        'xsi:type': Address._XSI_TYPE}],
                'cc': [{'address_value': "victim2@example.com",
                        'category': Address.CAT_EMAIL,
                        'xsi:type': Address._XSI_TYPE}],
                'bcc': [{'address_value': "victim3@example.com",
                        'category': Address.CAT_EMAIL,
                        'xsi:type': Address._XSI_TYPE}],
                'from': {'address_value': "badguy@attacker.com",
                        'category': Address.CAT_EMAIL,
                        'xsi:type': Address._XSI_TYPE},
                'subject': "This is not a malicious email",
                'in_reply_to': "<123456@mail.example.com>",
                'date': self.datetime_str,
                'message_id': "<abcdef@mail.attacker.com>",
                'sender': {'address_value': "attacker2@example.com",
                        'category': Address.CAT_EMAIL,
                        'xsi:type': Address._XSI_TYPE},
                'reply_to': {'address_value': "greyhat@attacker.com",
                        'category': Address.CAT_EMAIL,
                        'xsi:type': Address._XSI_TYPE},
                'errors_to': "/dev/null",
                'boundary': "----MIME_BOUNDARY------",
                'content_type': "mime/multi-part",
                'mime_version': "1.0",
                'precedence': "High",
                'user_agent': "Outlook_Express1.0",
                'x_mailer': "Outlook Express",
                'x_originating_ip': {'address_value': "1.2.3.4",
                                    'category': Address.CAT_IPV4,
                                    'xsi:type': Address._XSI_TYPE},
                'x_priority': 3,
            }
        self.maxDiff = None

        header = EmailHeader.from_dict(d)
        self.assertEqual(DateTime, type(header.date))
        d2 = cybox.test.round_trip_dict(EmailHeader, d)
        self.assertEqual(d, d2)

    def test_creation(self):
        header = EmailHeader()

        self.assertEqual(None, header.subject)
        header.subject = "Howdy"
        self.assertEqual(String, type(header.subject))

        self.assertEqual(None, header.date)
        header.date = self.datetime_str
        self.assertEqual(DateTime, type(header.date))
        self.assertEqual(datetime.datetime, type(header.date.value))

        self.assertEqual(None, header.message_id)
        header.message_id = "<1bc5nkmvakjn45mn@example.com>"
        self.assertEqual(String, type(header.message_id))


class TestEmailMessage(unittest.TestCase, ObjectTestCase):
    object_type = "EmailMessageObjectType"
    klass = EmailMessage

    def test_roundtrip_basic(self):
        msg_dict = {'header': {
                                'from': "sender@domain.org",
                                'to': ["recip@victim.org"],
                                'subject': "Howdy!"
                               },
                     'raw_body': "This is a test. This is only a test.",
                    }
        msg_obj = EmailMessage.object_from_dict(msg_dict)
        msg_dict2 = EmailMessage.dict_from_object(msg_obj)

        # Don't want to compare dictionaries directly since email addresses
        # will have been expanded to full dictionaries with "address_value"
        # and "category"
        self.assertEqual(msg_dict2['header']['from']['address_value'],
                         msg_dict['header']['from'])
        self.assertEqual(msg_dict2['header']['to'][0]['address_value'],
                         msg_dict['header']['to'][0])
        self.assertEqual(msg_dict2['header']['subject'],
                         msg_dict['header']['subject'])
        self.assertEqual(msg_dict2['raw_body'],
                         msg_dict['raw_body'])
        self.assertEqual(msg_dict2['xsi:type'], EmailMessage._XSI_TYPE)

        # Make sure extra keys didn't sneak into the output.
        self.assertFalse('attachments' in msg_dict2)
        self.assertFalse('optional_header' in msg_dict2)
        self.assertFalse('email_server' in msg_dict2)
        self.assertFalse('raw_header' in msg_dict2)
        self.assertFalse('cc' in msg_dict2['header'])
        self.assertFalse('bcc' in msg_dict2['header'])
        self.assertFalse('in_reply_to' in msg_dict2['header'])
        self.assertFalse('date' in msg_dict2['header'])
        self.assertFalse('message_id' in msg_dict2['header'])
        self.assertFalse('sender' in msg_dict2['header'])
        self.assertFalse('reply_to' in msg_dict2['header'])
        self.assertFalse('errors_to' in msg_dict2['header'])

    def test_from_date(self):
        date_str = "Thu, 14 Feb 2013 11:28:42 -0500"
        isoformat = "2013-02-14T11:28:42-05:00"

        d = {'header': {'date': date_str}}
        msg = EmailMessage.from_dict(d)
        self.assertEqual(msg.date.serialized_value, isoformat)


if __name__ == "__main__":
    unittest.main()
