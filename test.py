import unittest

from lexicrypt import Lexicrypt


class LexicryptTestCase(unittest.TestCase):

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
