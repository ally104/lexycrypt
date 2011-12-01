import unittest

import pymongo

from PIL import Image

from lexicrypt import Lexicrypt

connection = pymongo.Connection("localhost", 27017)
db = connection.lexicrypt


class LexicryptTestCase(unittest.TestCase):
 
    def tearDown(self):
        db.drop_collection('emails')

    def testAssignmentOfTokenToUser(self):
        """
        Validate that a user has a valid
        token set
        """
        lex = Lexicrypt()
        email = 'test@test.com'
        lex.get_or_create_email(email)
        db_emailer = db.emails.find_one({ 'email': email })

        assert email == db_emailer.get('email')
        assert db_emailer.get('token')

    def testValidDecryption(self):
        """
        Validate the encrypted text decrypts
        to the correct content via image
        """
        lex = Lexicrypt()
        message = u'this is the message'
        lex.encrypt_message(message, 'images/', 'test.png')
        dmessage = lex.decrypt_message('images/test.png')

        assert dmessage == message

    def testInvalidDecryption(self):
        """
        Validate the altered encrypted image
        decrypts incorrectly to the original text
        """
        lex = Lexicrypt()
        message = u'this is the message'
        lex.encrypt_message(message, 'images/', 'test.png')
        image = Image.open('images/test.png')
        putpixel = image.putpixel
        putpixel((0, 10), 255)
        putpixel((0, 11), 255)
        image.save('images/test.png')
        dmessage = lex.decrypt_message('images/test.png')

        assert dmessage != message
