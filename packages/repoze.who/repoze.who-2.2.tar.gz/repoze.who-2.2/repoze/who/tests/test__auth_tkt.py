import unittest

class _Base(unittest.TestCase):

    def failUnless(self, predicate, message=''):
        self.assertTrue(predicate, message) # Nannies go home!

    def failIf(self, predicate, message=''):
        self.assertFalse(predicate, message) # Nannies go home!

class AuthTicketTests(_Base):

    def _getTargetClass(self):
        from .._auth_tkt import AuthTicket
        return AuthTicket

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_ctor_defaults(self):
        from .. import _auth_tkt
        with _Monkey(_auth_tkt, time_mod=_Timemod):
            tkt = self._makeOne('SEEKRIT', 'USERID', '1.2.3.4')
        self.assertEqual(tkt.secret, 'SEEKRIT')
        self.assertEqual(tkt.userid, 'USERID')
        self.assertEqual(tkt.ip, '1.2.3.4')
        self.assertEqual(tkt.tokens, '')
        self.assertEqual(tkt.user_data, '')
        self.assertEqual(tkt.time, _WHEN)
        self.assertEqual(tkt.cookie_name, 'auth_tkt')
        self.assertEqual(tkt.secure, False)

    def test_ctor_explicit(self):
        tkt = self._makeOne('SEEKRIT', 'USERID', '1.2.3.4', tokens=('a', 'b'),
                            user_data='DATA', time=_WHEN,
                            cookie_name='oatmeal', secure=True)
        self.assertEqual(tkt.secret, 'SEEKRIT')
        self.assertEqual(tkt.userid, 'USERID')
        self.assertEqual(tkt.ip, '1.2.3.4')
        self.assertEqual(tkt.tokens, 'a,b')
        self.assertEqual(tkt.user_data, 'DATA')
        self.assertEqual(tkt.time, _WHEN)
        self.assertEqual(tkt.cookie_name, 'oatmeal')
        self.assertEqual(tkt.secure, True)

    def test_digest(self):
        from .._auth_tkt import calculate_digest
        tkt = self._makeOne('SEEKRIT', 'USERID', '1.2.3.4', tokens=('a', 'b'),
                            user_data='DATA', time=_WHEN,
                            cookie_name='oatmeal', secure=True)
        digest = calculate_digest('1.2.3.4', _WHEN, 'SEEKRIT', 'USERID',
                                  'a,b', 'DATA')
        self.assertEqual(tkt.digest(), digest)

    def test_cookie_value_wo_tokens_or_userdata(self):
        from .._auth_tkt import calculate_digest
        tkt = self._makeOne('SEEKRIT', 'USERID', '1.2.3.4', time=_WHEN)
        digest = calculate_digest('1.2.3.4', _WHEN, 'SEEKRIT', 'USERID', '', '')
        self.assertEqual(tkt.cookie_value(),
                         '%s%08xUSERID!' % (digest, _WHEN))

    def test_cookie_value_w_tokens_and_userdata(self):
        from .._auth_tkt import calculate_digest
        tkt = self._makeOne('SEEKRIT', 'USERID', '1.2.3.4', tokens=('a', 'b'),
                            user_data='DATA', time=_WHEN)
        digest = calculate_digest('1.2.3.4', _WHEN, 'SEEKRIT', 'USERID',
                                  'a,b', 'DATA')
        self.assertEqual(tkt.cookie_value(),
                         '%s%08xUSERID!a,b!DATA' % (digest, _WHEN))

    def test_cookie_not_secure_wo_tokens_or_userdata(self):
        from .._auth_tkt import calculate_digest
        from .._compat import encodestring
        tkt = self._makeOne('SEEKRIT', 'USERID', '1.2.3.4', time=_WHEN,
                            cookie_name='oatmeal')
        digest = calculate_digest('1.2.3.4', _WHEN, 'SEEKRIT', 'USERID', '', '')
        cookie = tkt.cookie()
        self.assertEqual(cookie['oatmeal'].value,
                         encodestring('%s%08xUSERID!' % (digest, _WHEN)
                                     ).strip())
        self.assertEqual(cookie['oatmeal']['path'], '/')
        self.assertEqual(cookie['oatmeal']['secure'], '')

    def test_cookie_secure_w_tokens_and_userdata(self):
        from .._auth_tkt import calculate_digest
        from .._compat import encodestring
        tkt = self._makeOne('SEEKRIT', 'USERID', '1.2.3.4', tokens=('a', 'b'),
                            user_data='DATA', time=_WHEN,
                            cookie_name='oatmeal', secure=True)
        digest = calculate_digest('1.2.3.4', _WHEN, 'SEEKRIT', 'USERID',
                                  'a,b', 'DATA')
        cookie = tkt.cookie()
        self.assertEqual(cookie['oatmeal'].value,
                         encodestring('%s%08xUSERID!a,b!DATA' % (digest, _WHEN)
                                     ).strip())
        self.assertEqual(cookie['oatmeal']['path'], '/')
        self.assertEqual(cookie['oatmeal']['secure'], 'true')
 

class BadTicketTests(_Base):

    def _getTargetClass(self):
        from .._auth_tkt import BadTicket
        return BadTicket

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_wo_expected(self):
        exc = self._makeOne('message')
        self.assertEqual(exc.args, ('message',))
        self.assertEqual(exc.expected, None)

    def test_w_expected(self):
        exc = self._makeOne('message', 'foo')
        self.assertEqual(exc.args, ('message',))
        self.assertEqual(exc.expected, 'foo')


class Test_parse_ticket(_Base):

    def _callFUT(self, secret='SEEKRIT', ticket=None, ip='1.2.3.4'):
        from .._auth_tkt import parse_ticket
        return parse_ticket(secret, ticket, ip)

    def test_bad_timestamp(self):
        from .._auth_tkt import BadTicket
        TICKET = '12345678901234567890123456789012XXXXXXXXuserid!'
        try:
            self._callFUT(ticket=TICKET)
        except BadTicket as e:
            self.failUnless(e.args[0].startswith(
                            'Timestamp is not a hex integer:'))
        else:
            self.fail('Did not raise')

    def test_no_bang_after_userid(self):
        from .._auth_tkt import BadTicket
        TICKET = '1234567890123456789012345678901201020304userid'
        try:
            self._callFUT(ticket=TICKET)
        except BadTicket as e:
            self.assertEqual(e.args[0], 'userid is not followed by !')
        else:
            self.fail('Did not raise')

    def test_wo_tokens_or_data_bad_digest(self):
        from .._auth_tkt import BadTicket
        TICKET = '1234567890123456789012345678901201020304userid!'
        try:
            self._callFUT(ticket=TICKET)
        except BadTicket as e:
            self.assertEqual(e.args[0], 'Digest signature is not correct')
        else:
            self.fail('Did not raise')

    def test_wo_tokens_or_data_ok_digest(self):
        from .._auth_tkt import calculate_digest
        digest = calculate_digest('1.2.3.4', _WHEN, 'SEEKRIT', 'USERID', '', '')
        TICKET = '%s%08xUSERID!' % (digest, _WHEN)
        timestamp, userid, tokens, user_data = self._callFUT(ticket=TICKET)
        self.assertEqual(timestamp, _WHEN)
        self.assertEqual(userid, 'USERID')
        self.assertEqual(tokens, [''])
        self.assertEqual(user_data, '')

    def test_w_tokens_and_data_ok_digest(self):
        from .._auth_tkt import calculate_digest
        digest = calculate_digest('1.2.3.4', _WHEN, 'SEEKRIT', 'USERID',
                                  'a,b', 'DATA')
        TICKET = '%s%08xUSERID!a,b!DATA' % (digest, _WHEN)
        timestamp, userid, tokens, user_data = self._callFUT(ticket=TICKET)
        self.assertEqual(timestamp, _WHEN)
        self.assertEqual(userid, 'USERID')
        self.assertEqual(tokens, ['a', 'b'])
        self.assertEqual(user_data, 'DATA')


class Test_helpers(_Base):

    # calculate_digest is not very testable, and fully exercised throug callers.

    def test_ints_to_bytes(self):
        from struct import pack
        from .._auth_tkt import ints2bytes
        self.assertEqual(ints2bytes([1, 2, 3, 4]), pack('>BBBB', 1, 2, 3, 4))
        
    def test_encode_ip_timestamp(self):
        from struct import pack
        from .._auth_tkt import encode_ip_timestamp
        self.assertEqual(encode_ip_timestamp('1.2.3.4', _WHEN),
                         pack('>BBBBL', 1, 2, 3, 4, _WHEN))

    def test_maybe_encode_bytes(self):
        from .._auth_tkt import maybe_encode
        foo = b'foo'
        self.failUnless(maybe_encode(foo) is foo)

    def test_maybe_encode_native_string(self):
        from .._auth_tkt import maybe_encode
        foo = 'foo'
        self.assertEqual(maybe_encode(foo), b'foo')

    def test_maybe_encode_unicode(self):
        from .._auth_tkt import maybe_encode
        from .._compat import u
        foo = u('foo')
        self.assertEqual(maybe_encode(foo), b'foo')


_WHEN = 1234567
class _Timemod(object):
    @staticmethod
    def time():
        return _WHEN


class _Monkey(object):

    def __init__(self, module, **replacements):
        self.module = module
        self.orig = {}
        self.replacements = replacements
        
    def __enter__(self):
        for k, v in self.replacements.items():
            orig = getattr(self.module, k, self)
            if orig is not self:
                self.orig[k] = orig
            setattr(self.module, k, v)

    def __exit__(self, *exc_info):
        for k, v in self.replacements.items():
            if k in self.orig:
                setattr(self.module, k, self.orig[k])
            else: #pragma NO COVERSGE
                delattr(self.module, k)
