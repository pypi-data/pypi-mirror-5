
import unittest
from email.message import Message

from slimta.envelope import Envelope
from slimta.bounce import Bounce
from slimta.smtp.reply import Reply


class TestEnvelope(unittest.TestCase):

    def test_copy(self):
        env1 = Envelope('sender@example.com', ['rcpt1@example.com'])
        env1.parse("""\
From: sender@example.com
To: rcpt1@example.com

test test
""".replace('\n', '\r\n'))
        env2 = env1.copy()
        env2.recipients.append('rcpt2@example.com')
        env2.headers['To'] = 'rcpt2@example.com'
        self.assertEqual('sender@example.com', env1.sender)
        self.assertEqual(['rcpt1@example.com'], env1.recipients)
        self.assertEqual(['rcpt1@example.com'], env1.headers.get_all('To'))
        self.assertEqual('sender@example.com', env2.sender)
        self.assertEqual(['rcpt1@example.com', 'rcpt2@example.com'], env2.recipients)
        self.assertEqual(['rcpt1@example.com', 'rcpt2@example.com'], env2.headers.get_all('To'))

    def test_repr(self):
        env = Envelope('sender@example.com')
        s = repr(env)
        self.assertRegexpMatches(s, r"<Envelope at 0x[a-fA-F0-9]+, sender='sender@example.com'>")

    def test_flatten(self):
        headers = Message()
        headers['From'] = 'sender@example.com'
        headers['To'] = 'rcpt1@example.com'
        headers['To'] = 'rcpt2@example.com'
        body = 'test test\r\n'
        env = Envelope(headers=headers, message=body)
        header_str = '\r\n'.join(['From: sender@example.com',
                                  'To: rcpt1@example.com',
                                  'To: rcpt2@example.com',
                                  '', ''])
        ret_headers, ret_body = env.flatten()
        self.assertEqual(header_str, ret_headers)
        self.assertEqual(body, ret_body)

    def test_parse(self):
        env = Envelope()
        env.parse("""\
From: sender@example.com
To: rcpt1@example.com
To: rcpt2@example.com

test test\r
""")
        self.assertEqual('sender@example.com', env.headers['from'])
        self.assertEqual(['rcpt1@example.com', 'rcpt2@example.com'],
                         env.headers.get_all('To'))
        self.assertEquals('test test\r\n', env.message)

    def test_parse_onlyheaders(self):
        env = Envelope()
        env.parse("""\
From: sender@example.com
Subject: important things
""")
        self.assertEqual('sender@example.com', env.headers['from'])
        self.assertEqual('important things', env.headers['subject'])
        self.assertEqual('', env.message)

    def test_parse_message_object(self):
        data = Message()
        data['From'] = 'sender@example.com'
        data['To'] = 'rcpt1@example.com'
        data['To'] = 'rcpt2@example.com'
        data.set_payload('test test\r\n')
        env = Envelope()
        env.parse(data)
        self.assertEqual('sender@example.com', env.headers['from'])
        self.assertEqual(['rcpt1@example.com', 'rcpt2@example.com'], env.headers.get_all('to'))
        self.assertEqual('test test\r\n', env.message)

    def test_bounce(self):
        env = Envelope('sender@example.com', ['rcpt1@example.com',
                                              'rcpt2@example.com'])
        env.parse("""\
From: sender@example.com
To: rcpt1@example.com
To: rcpt2@example.com

test test\r
""")
        reply = Reply('550', '5.0.0 Rejected')

        Bounce.header_template = """\
X-Reply-Code: {code}
X-Reply-Message: {message}
X-Orig-Sender: {sender}

"""
        Bounce.footer_template = """\

EOM
"""
        bounce = Bounce(env, reply)

        self.assertEqual('', bounce.sender)
        self.assertEqual(['sender@example.com'], bounce.recipients)
        self.assertEqual('550', bounce.headers['X-Reply-Code'])
        self.assertEqual('5.0.0 Rejected', bounce.headers['X-Reply-Message'])
        self.assertEqual('sender@example.com', bounce.headers['X-Orig-Sender'])
        self.assertEqual("""\
From: sender@example.com\r
To: rcpt1@example.com\r
To: rcpt2@example.com\r
\r
test test\r

EOM
""", bounce.message)

    def test_bounce_headersonly(self):
        env = Envelope('sender@example.com', ['rcpt1@example.com',
                                              'rcpt2@example.com'])
        env.parse("""\
From: sender@example.com
To: rcpt1@example.com
To: rcpt2@example.com

test test\r
""")
        reply = Reply('550', '5.0.0 Rejected')

        Bounce.header_template = """\
X-Reply-Code: {code}
X-Reply-Message: {message}
X-Orig-Sender: {sender}

"""
        Bounce.footer_template = """\
\r
EOM\r
"""
        bounce = Bounce(env, reply, headers_only=True)

        self.assertEqual('', bounce.sender)
        self.assertEqual(['sender@example.com'], bounce.recipients)
        self.assertEqual('550', bounce.headers['X-Reply-Code'])
        self.assertEqual('5.0.0 Rejected', bounce.headers['X-Reply-Message'])
        self.assertEqual('sender@example.com', bounce.headers['X-Orig-Sender'])
        self.assertEqual("""\
From: sender@example.com\r
To: rcpt1@example.com\r
To: rcpt2@example.com\r
\r
\r
EOM\r
""", bounce.message)

# vim:et:fdm=marker:sts=4:sw=4:ts=4
