import os
import random

from Crypto.Cipher import AES
from PIL import Image

import settings

AES = AES.new(settings.SECRET_KEY, AES.MODE_ECB)
BLOCK_SIZE = 16
IMAGE_WIDTH = 50
RGB = 255


class Lexicrypt():
    """
    All the encryption/decryption functionality
    for text and images
    """

    def __init__(self):
        self.char_array = []

    def encrypt_message(self, message, image_path, filename):
        """
        Encrypt a block of text.
        Currently testing with AES
        """
        cipher_text = AES.encrypt(self._pad_message(message))
        image = self._generate_image(cipher_text, image_path, filename)
        return image

    def decrypt_message(self, image_path):
        """
        Load the image.
        Decrypt a block of text.
        Currently testing with AES
        """
        message = ''
        image = Image.open(image_path).getdata()
        width, height = image.size
        for y in range(height):
            c = image.getpixel((0, y))
            try:
                c_idx = [v[1] for v in self.char_array].index(c)
                message += self.char_array[c_idx][0]
            except ValueError:
                print 'Image decryption failed: image data corrupt.'
                return False
        cipher_text = AES.decrypt(message).strip()
        return cipher_text

    def _pad_message(self, message):
        """
        Verify that the message is
        in a multiple of 16
        """
        message_length = len(message)
        if message_length < BLOCK_SIZE:
            message = message.ljust(BLOCK_SIZE - message_length)
        else:
            if message_length % BLOCK_SIZE != 0:
                current_count = message_length
                while(current_count % BLOCK_SIZE != 0):
                    message = "%s " % message
                    current_count += 1
        return message

    def _generate_image(self, cipher_text, image_path, filename):
        """
        Assign each character with a specific
        colour.
        """
        cipher_length = len(cipher_text)
        image = Image.new('RGBA', (IMAGE_WIDTH, cipher_length))

        putpixel = image.im.putpixel
        char_array = [v[0] for v in self.char_array]
        for idx, c in enumerate(cipher_text):
            if c in char_array:
                c_idx = char_array.index(c)
                rgb = self.char_array[c_idx][1]
            else:
                rgb = self._generate_rgb(c)
                self.char_array.append((c, rgb))
            for i in range(IMAGE_WIDTH):
                putpixel((i, idx), rgb)
        image_full_path = os.path.join(image_path, filename)
        image.save(image_full_path)

    def _generate_rgb(self, c):
        """
        Generate the RGB values for this
        character. If the RGB value is already
        taken, try again
        """
        rgb = (random.randint(0, RGB),
               random.randint(0, RGB),
               random.randint(0, RGB),
               random.randint(0, RGB))
        if c in [v[1] for v in self.char_array]:
            # call this function again until we are happy
            self._generate_rgb()
        else:
            return rgb
