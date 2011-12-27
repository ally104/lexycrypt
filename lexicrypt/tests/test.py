# -*- coding: utf-8 -*-
import unittest

from PIL import Image

from ..lexicrypt import Lexicrypt

from .. import settings

lex = Lexicrypt()
lex.set_environment('test')


class LexicryptTestCase(unittest.TestCase):
    def tearDown(self):
        lex.db.drop_collection('messages')
        lex.db.drop_collection('users')

    def testAssignmentOfTokenToUser(self):
        """Validate that a user has a valid
        token set.
        """
        email = 'test@test.com'
        email_mixed1 = '1TeSt@teSt.com'
        email_mixed2 = 'TeSt@teSt.com'
        lex.get_or_create_email(email)
        lex.get_or_create_email(email_mixed1)
        lex.get_or_create_email(email_mixed2)
        db_emailer = lex.db.users.find_one({'email': email})

        assert email == db_emailer['email']
        assert lex.db.users.count() == 2
        assert db_emailer['token']

    def testAccessTokensAddedToMessage(self):
        """Validate that access tokens can be added to
        a message for the author and that they can
        decrypt the content.
        """
        sender = 'test@test.com'
        sender_token = lex.get_or_create_email(sender)['token']
        message = u'this is the message'
        lex.encrypt_message(message,
                            'lexicrypt/tests/images/',
                            'test.png',
                            sender_token)
        receiver1 = 'test2@test.com'
        receiver2 = 'test3@test.com'
        lex.add_email_accessor(
                'lexicrypt/tests/images/test.png', receiver1, sender_token)
        lex.add_email_accessor(
                'lexicrypt/tests/images/test.png', receiver2, sender_token)
        accessor1 = lex.db.users.find_one({'email': receiver1})
        accessor2 = lex.db.users.find_one({'email': receiver2})

        assert accessor1['email'] == receiver1
        assert accessor2['email'] == receiver2

    def testDeleteAccessToken(self):
        """Validate that a deleted access token loses
        decryption access to the message.
        """
        sender = 'test@test.com'
        sender_token = lex.get_or_create_email(sender)
        message = u'this is the message 汉字/漢字 hànzì'
        lex.encrypt_message(message,
                            'lexicrypt/tests/images/',
                            'test.png',
                            sender_token)
        receiver1 = 'test2@test.com'
        receiver2 = 'test3@test.com'
        lex.add_email_accessor('lexicrypt/tests/images/test.png',
                               receiver1, sender_token)
        lex.add_email_accessor('lexicrypt/tests/images/test.png',
                               receiver2, sender_token)
        lex.remove_email_accessor('lexicrypt/tests/images/test.png',
                                  receiver1,
                                  sender_token)
        message = lex.db.messages.find_one({'message':
                                            'lexicrypt/tests/images/test.png'})
        accessor = False

        if message and receiver1 in message['accessors']:
            accessor = True

        assert not accessor

    def testValidDecryption(self):
        """Validate the encrypted text decrypts
        to the correct content via image. Accessor
        of message must be an owner of the message or have
        their token in the access list for the messages.
        """
        email = 'test@test.com'
        sender_token = lex.get_or_create_email(email)['token']
        message1 = u'this is the message1'
        lex.encrypt_message(message1, 'lexicrypt/tests/images/',
                            'test.png', sender_token)
        receiver1 = 'test2@test.com'
        r_email1 = lex.get_or_create_email(receiver1)
        lex.add_email_accessor('lexicrypt/tests/images/test.png',
                               receiver1,
                               sender_token)
        dmessage1 = lex.decrypt_message('lexicrypt/tests/images/test.png',
                                        r_email1['token'])

        assert dmessage1 == message1

        message2 = u'this is the message2'
        lex.encrypt_message(message2, 'lexicrypt/tests/images/',
                            'test2.png', sender_token)
        receiver2 = 'test3@test.com'
        r_email2 = lex.get_or_create_email(receiver2)
        lex.add_email_accessor('lexicrypt/tests/images/test2.png',
                               receiver2,
                               sender_token)
        dmessage2 = lex.decrypt_message('lexicrypt/tests/images/test2.png',
                                        r_email2['token'])

        assert dmessage2 == message2

    def testInvalidEncryption(self):
        """Validate that a user passes an
        existing token before anything can
        be encrypted.
        """
        message = u'this is the message'

        assert not lex.encrypt_message(message, 'lexicrypt/tests/images/',
                                       'test.png', '1111')

    def testInvalidDecryption(self):
        """Validate the altered encrypted image
        decrypts incorrectly to the original text.
        """
        email = 'test@test.com'
        sender_token = lex.get_or_create_email(email)['token']
        message = u'this is the message'
        lex.encrypt_message(message, 'lexicrypt/tests/images/',
                            'test.png', sender_token)
        image = Image.open('lexicrypt/tests/images/test.png')
        putpixel = image.putpixel
        putpixel((0, 10), 255)
        putpixel((0, 11), 255)
        image.save('lexicrypt/tests/images/test.png')
        invalid_access_token = '111111'
        dmessage = lex.decrypt_message('lexicrypt/tests/images/test.png',
                                       invalid_access_token)

        assert not dmessage
        assert dmessage != message

    def testValidDeleteMessage(self):
        """Validate that only the author of the message
        can delete it.
        """
        sender_token = lex.get_or_create_email('test@test.com')
        message = u'this is the message'
        lex.encrypt_message(message, 'lexicrypt/tests/images/',
                            'test.png', sender_token['token'])
        other_token = lex.get_or_create_email('test2@test.com')
        
        lex.delete_message('lexicrypt/tests/images/test.png',
                           other_token['token'])
        message = lex.db.messages.find_one({'message':
                'lexicrypt/tests/images/test.png'})
        
        assert message
    
        lex.delete_message('lexicrypt/tests/images/test.png',
                           sender_token['token'])
        message = lex.db.messages.find_one({'message':
                'lexicrypt/tests/images/test.png'})

        assert not message
