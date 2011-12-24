# -*- coding: utf-8 -*-
import ast
import base64
import os
import random
import time

from Crypto.Cipher import AES
from PIL import Image

import settings

AES = AES.new(settings.SECRET_KEY, AES.MODE_ECB)
BLOCK_SIZE = 16
IMAGE_WIDTH = 50
RGB = 255

if settings.ENV == 'test':
    db = settings.TEST_DATABASE
else:
    db = settings.DATABASE


class Lexicrypt():
    """All the encryption/decryption functionality
    for text and images
    """
    def __init__(self):
        self.char_array = []

    def get_or_create_email(self, email):
        """Find the email address in the system
        or create it if it doesn't exist.
        """
        email = email.lower().strip()
        if not db.users.find_one({ "email": email }):
            db.users.update({ "email": email },
                            { "$set": { "token": self._generate_token(email) }},
                            upsert=True)
        emailer = db.users.find_one({ "email": email })
        self.token = emailer['token']
        self.email = email
        return emailer
    
    def add_email_accessor(self, image_path, email, sender_token):
        """Add the email to the access list for
        the message.
        """
        sender_token = db.users.find_one({ "token": sender_token })
        if sender_token:
            email = email.lower().strip()
            accessor = self.get_or_create_email(email)
            db.messages.update({ "message": image_path },
                               { "$set": { "token": sender_token }},
                               upsert=True)
            db.messages.update({ "message": image_path, "token": sender_token, },
                               { "$addToSet": { "accessors": accessor['token'] }},
                               upsert=True)
            return accessor['token']
        else:
            return False

    def remove_email_accessor(self, image_path, email, sender_token):
        """Remove an email from the access list for
        the message.
        """
        sender_token = db.users.find_one({ "token": sender_token })
        if sender_token:
            email = email.lower().strip()
            accessor = db.users.find_one({ "email": email })
            db.messages.update({ "message": image_path, "token": sender_token },
                               { "$pull": { "accessors": accessor['token'] }})
    
    def is_accessible(self, image_path, accessor_token):
        """Check to see if the user can access the image"""
        accessor = db.users.find_one({ "token": accessor_token })
        if accessor:
            message = db.messages.find_one({ "message": image_path })
            if accessor['token'] in message['accessors']:
                return True
        return False

    def encrypt_message(self, message, image_path, filename, sender_token):
        """Encrypt a block of text.
        Currently testing with AES.
        """
        sender_token = db.users.find_one({ "token": sender_token })
        if sender_token:
            cipher_text = AES.encrypt(self._pad_message(unicode(message).encode('utf-8')))
            image = self._generate_image(cipher_text, image_path, filename)
            return image
        else:
            return False

    def decrypt_message(self, image_path, accessor_token):
        """Load the image.
        Decrypt a block of text.
        Currently testing with AES.
        """
        message = db.messages.find_one({ "message": image_path })
        if accessor_token in message['accessors']:
            result_map = base64.b64decode(message['result_map'])
            result_map = ast.literal_eval(result_map)
            message = ''
            image = Image.open(image_path).getdata()
            width, height = image.size
            for y in range(height):
                c = image.getpixel((0, y))
                try:
                    c_idx = [v[1] for v in result_map].index(c)
                    message += result_map[c_idx][0]
                except ValueError:
                    print 'Image decryption failed: image data corrupt.'
                    return False
            cipher_text = AES.decrypt(message).strip()
            return cipher_text
        else:
            return False

    def _pad_message(self, message):
        """Verify that the message is in a multiple of 16."""
        message_length = len(message)
        if message_length < BLOCK_SIZE:
            message = message.ljust(BLOCK_SIZE)
        else:
            if message_length % BLOCK_SIZE != 0:
                current_count = message_length
                while(current_count % BLOCK_SIZE != 0):
                    message = "%s " % message
                    current_count += 1
        return message

    def _generate_image(self, cipher_text, image_path, filename):
        """Assign each character with a specific
        colour. Also save the token for the sender.
        """
        cipher_length = len(cipher_text)
        image = Image.new('RGB', (IMAGE_WIDTH, cipher_length))
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
        if settings.ENV == 'test':
            image_full_path = '%s%s' % (image_path, filename)
        else:
            image_full_path = os.path.join(image_path, filename)
        image.save(image_full_path)

        db.messages.update({ "message": image_full_path },
                           { "$set": { "result_map": base64.b64encode(str(self.char_array)) }},
                           upsert=True)
        db.messages.update({ "message": image_full_path },
                           { "$addToSet": { "accessors": self.token }},
                           upsert=True)
        self.char_array = []
        return image_full_path

    def _generate_rgb(self, c):
        """Generate the RGB values for this
        character. If the RGB value is already
        taken, try again.
        """
        rgb = (random.randint(0, RGB),
               random.randint(0, RGB),
               random.randint(0, RGB))
        if c in [v[1] for v in self.char_array]:
            # call this function again until we are happy
            self._generate_rgb()
        else:
            return rgb
    
    def _generate_token(self, email):
        """Generate a token based on the timestamp
        and the user's email address.
        """
        random_int = str(random.randrange(100, 10000))
        token_string = '%s%s%s' % (random_int,
                                   email,
                                   str(int(time.time())))
        return base64.b64encode(token_string)
