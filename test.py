import unittest

from PIL import Image

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
