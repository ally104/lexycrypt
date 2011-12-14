import unittest

from PIL import Image

from ..lexicrypt import Lexicrypt

from .. import settings

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
        lex.encrypt_message(message, 'lexicrypt/tests/images/', 'test.png')
        receiver1 = 'test2@test.com'
        receiver2 = 'test3@test.com'
        receiver_token1 = lex.add_email_accessor('lexicrypt/tests/images/test.png', receiver1)
        receiver_token2 = lex.add_email_accessor('lexicrypt/tests/images/test.png', receiver2)
        accessor1 = db.emails.find_one({ "email": receiver1 })
        accessor2 = db.emails.find_one({ "email": receiver2 })

        assert accessor1['token'] == receiver_token1
        assert accessor2['token'] == receiver_token2

    def testDeleteAccessToken(self):
        """
        Validate taht a deleted access token loses decryption
        access to the message
        """
        lex = Lexicrypt()
        sender = 'test@test.com'
        lex.get_or_create_email(sender)
        message = u'this is the message'
        lex.encrypt_message(message, 'lexicrypt/tests/images/', 'test.png')
        receiver1 = 'test2@test.com'
        receiver2 = 'test3@test.com'
        receiver_token1 = lex.add_email_accessor('lexicrypt/tests/images/test.png', receiver1)
        receiver_token2 = lex.add_email_accessor('lexicrypt/tests/images/test.png', receiver2)
        lex.remove_email_accessor('lexicrypt/tests/images/test.png', receiver1)
        accessor_tokens = db.emails.find_one({ "messages.message": 'lexicrypt/tests/images/test.png' })['accessors']

        assert receiver1 not in accessor_tokens

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
        message1 = u'this is the message1'
        message2 = u'this is the message2'
        lex.encrypt_message(message1, 'lexicrypt/tests/images/', 'test.png')
        lex.encrypt_message(message2, 'lexicrypt/tests/images/', 'test2.png')
        receiver1 = 'test2@test.com'
        receiver2 = 'test3@test.com'
        receiver_token1 = lex.add_email_accessor('lexicrypt/tests/images/test.png', receiver1)
        receiver_token2 = lex.add_email_accessor('lexicrypt/tests/images/test2.png', receiver2)
        dmessage1 = lex.decrypt_message('lexicrypt/tests/images/test.png', receiver_token1)
        dmessage2 = lex.decrypt_message('lexicrypt/tests/images/test2.png', receiver_token2)
        db_emailer = db.emails.find_one({ "email": email })

        assert dmessage1 == message1
        assert dmessage2 == message2
        assert { 'message': 'lexicrypt/tests/images/test.png' } in db_emailer['messages']
        assert { 'message': 'lexicrypt/tests/images/test2.png' } in db_emailer['messages']
        assert db_emailer['email'] == email
    
    def testInvalidEncryption(self):
        """
        Validate that a user passes an
        existing token before anything can
        be encrypted
        """
        lex = Lexicrypt()
        message = u'this is the message'

        assert not lex.encrypt_message(message, 'lexicrypt/tests/images/', 'test.png')

    def testInvalidDecryption(self):
        """
        Validate the altered encrypted image
        decrypts incorrectly to the original text.
        """
        lex = Lexicrypt()
        email = 'test@test.com'
        lex.get_or_create_email(email)
        message = u'this is the message'
        lex.encrypt_message(message, 'lexicrypt/tests/images/', 'test.png')
        image = Image.open('lexicrypt/tests/images/test.png')
        putpixel = image.putpixel
        putpixel((0, 10), 255)
        putpixel((0, 11), 255)
        image.save('lexicrypt/tests/images/test.png')
        invalid_access_token = '111111'
        dmessage = lex.decrypt_message('lexicrypt/tests/images/test.png', invalid_access_token)

        assert not dmessage
        assert dmessage != message
