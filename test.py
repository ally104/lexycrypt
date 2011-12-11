import unittest

import pymongo

from PIL import Image

import settings

from lexicrypt import Lexicrypt

import settings

db = settings.DATABASE


class LexicryptTestCase(unittest.TestCase):
    def tearDown(self):
        db.drop_collection('emails')

    def testAssignmentOfTokenToUser(self):
        """
        Validate that a user has a valid
        token set.
        """
        lex = Lexicrypt()
        email = 'test@test.com'
        email_mixed1 = '1TeSt@teSt.com'
        email_mixed2 = 'TeSt@teSt.com'
        lex.get_or_create_email(email)
        lex.get_or_create_email(email_mixed1)
        lex.get_or_create_email(email_mixed2)
        db_emailer = db.emails.find({ "email": email })

        assert email == db_emailer[0].get('email')
        assert db.emails.count() == 2
        assert db_emailer[0].get('token')

    def testAccessTokensAddedToMessage(self):
        """
        Validate that access tokens can be added to
        a message for the author and that they can
        decrypt the content.
        """
        lex = Lexicrypt()
        sender = 'test@test.com'
        lex.get_or_create_email(sender)
        message = u'this is the message'
        lex.encrypt_message(message, 'images/', 'test.png')
        receiver = 'test2@test.com'
        receiver_token = lex.add_email_accessor('images/test.png', receiver)
        accessor = db.emails.find_one({ "email": receiver })

        assert accessor['token'] == receiver_token

    def testValidDecryption(self):
        """
        Validate the encrypted text decrypts
        to the correct content via image. Accessor
        of message must be an owner of the message or have
        their token in the access list for the messages.
        """
        lex = Lexicrypt()
        email = 'test@test.com'
        lex.get_or_create_email(email)
        message = u'this is the message'
        lex.encrypt_message(message, 'images/', 'test.png')
        receiver = 'test2@test.com'
        receiver_token = lex.add_email_accessor('images/test.png', receiver)
        dmessage = lex.decrypt_message('images/test.png', receiver_token)
        db_emailer = db.emails.find_one({ "email": email })

        assert dmessage == message
        assert db_emailer['messages']['message'] == 'images/test.png'
        assert db_emailer['email'] == email
    
    def testInvalidEncryption(self):
        """
        Validate that a user passes an
        existing token before anything can
        be encrypted
        """
        lex = Lexicrypt()
        message = u'this is the message'

        assert not lex.encrypt_message(message, 'images/', 'test.png')

    def testInvalidDecryption(self):
        """
        Validate the altered encrypted image
        decrypts incorrectly to the original text.
        """
        lex = Lexicrypt()
        email = 'test@test.com'
        lex.get_or_create_email(email)
        message = u'this is the message'
        lex.encrypt_message(message, 'images/', 'test.png')
        image = Image.open('images/test.png')
        putpixel = image.putpixel
        putpixel((0, 10), 255)
        putpixel((0, 11), 255)
        image.save('images/test.png')
        invalid_access_token = '111111'
        dmessage = lex.decrypt_message('images/test.png', invalid_access_token)

        assert not dmessage
        assert dmessage != message
