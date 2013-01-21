# -*- coding: utf-8 -*-
import ast
import base64
import bson
import os
import random
import time
import urllib2

from boto.s3.key import Key
from bson.objectid import ObjectId
from cStringIO import StringIO
from Crypto.Cipher import AES
from PIL import Image
from pymongo import DESCENDING

import settings

AES = AES.new(settings.SECRET_KEY, AES.MODE_ECB)
BLOCK_SIZE = 16
IMAGE_WIDTH = 50
RGB = 255


class Lexicrypt():
    """All the encryption/decryption functionality
    for text and images.
    """
    def __init__(self):
        self.char_array = []
        self.token = ''
        self.env = 'dev'
        self.db = settings.DATABASE

    def set_environment(self, env='dev'):
        if env == 'test':
            self.env = env
            self.db = settings.TEST_DATABASE

    def get_or_create_email(self, email):
        """Find the email address in the system
        or create it if it doesn't exist.
        """
        email = email.lower().strip()
        if not self.db.users.find_one({"email":email}):
            self.db.users.update({"email":email},
                                 {"$set":{"token":self._generate_token(email)}},
                                  upsert=True)
        emailer = self.db.users.find_one({"email":email})
        self.token = emailer['token']
        return emailer

    def get_email_by_token(self, token):
        """Return user's email by token reference"""
        emailer = self.db.users.find_one({"token":token})
        if emailer:
            return emailer['email']

    def add_email_accessor(self, image_path, email, sender_token):
        """Add the email to the access list for
        the message, only if the message exists.
        """
        if len(email.strip()) < 3:
            return False
        user_token = self.db.messages.find({"message":image_path,
                                            "token":sender_token})
        if user_token:
            accessor = self.get_or_create_email(email)
            self.db.messages.update({"message":image_path},
                               {"$set": {"token":sender_token}},
                               upsert=True)
            self.db.messages.update({"message":image_path, "token":sender_token},
                               {"$addToSet":{"accessors":accessor['token']}},
                               upsert=True)
            return accessor['token']
        else:
            return False

    def get_messages(self, sender_token=None, limit=20):
        """Get all messages sorted by created_at descending.
        If a sender_token is supplied, get all the user's
        encrypted messages.
        """
        try:
            if sender_token:
                messages = self.db.messages.find({
                        "token": sender_token}).sort("created_at", DESCENDING).limit(int(limit))
            else:
                messages = self.db.messages.find().sort("created_at", DESCENDING).limit(int(limit))
        except TypeError:
            messages = []
        return messages

    def get_message(self, id):
        """Retrieve a single message"""
        try:
            message = self.db.messages.find_one({"_id":ObjectId(id)})
            return message
        except bson.errors.InvalidId:
            return False

    def remove_email_accessor(self, image_path, email, sender_token):
        """Remove an email from the access list for the message."""
        sender_token = self.db.users.find({"message":image_path,
                                           "token":sender_token})
        if sender_token:
            email = email.lower().strip()
            accessor = self.db.users.find_one({"email":email})
            self.db.messages.update({"message":image_path},
                                    {"$pull": {"accessors":accessor['token']}})

    def is_accessible(self, image_path, accessor_token):
        """Check to see if the user can access the image"""
        accessor = self.db.users.find_one({"token":accessor_token})
        if accessor:
            message = self.db.messages.find_one({"message":image_path})
            if accessor['token'] in message['accessors']:
                return True
        return False

    def encrypt_message(self, message, image_path, filename, sender_token):
        """Encrypt a block of text.
        Currently testing with AES and truncating to 250 characters.
        """
        sender_token = self.db.users.find_one({"token":sender_token})
        if sender_token:
            cipher_text = AES.encrypt(self._pad_message(
                    unicode(message[:250]).encode('utf-8')))
            image = self._generate_image(cipher_text, image_path,
                    filename, sender_token['token'])
            return image
        else:
            return False

    def decrypt_message(self, image_path, accessor_token):
        """Load the image and decrypt the block of text.
        If it fails, return an empty string rather than False.
        """

        try:
            message = self.db.messages.find_one({"message":image_path})
            if accessor_token in message['accessors']:
                result_map = base64.b64decode(message['result_map'])
                result_map = ast.literal_eval(result_map)
                message = ''
                if self.env == 'test':
                    image = Image.open(image_path).getdata()
                else:
                    im = StringIO(urllib2.urlopen(image_path).read())
                    image = Image.open(im).getdata()
                width, height = image.size
                for y in range(height):
                    c = image.getpixel((0, y))
                    try:
                        c_idx = [v[1] for v in result_map].index(c)
                        message += result_map[c_idx][0]
                    except ValueError:
                        print 'Image decryption failed: image data corrupt.'
                        return ''
                cipher_text = AES.decrypt(message).strip()
                return cipher_text
            else:
                return ''
        except TypeError:
            raise

    def delete_message(self, image_path, sender_token):
        """Delete message."""
        message_token = self.db.messages.find({"message":image_path,
                                               "token":sender_token})
        if message_token:
            self.db.messages.remove({"message":image_path, "token":sender_token})
            return True
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

    def _generate_image(self, cipher_text, image_path, filename, sender_token):
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
        if self.env == 'test':
            image_full_path = '%s%s' % (image_path, filename)
            image.save(image_full_path)
        else:
            image_full_path = os.path.join(image_path, filename)
            image.save(image_full_path)
            aws_key = Key(settings.BUCKET)
            aws_key.key = filename
            aws_key.set_contents_from_filename(image_full_path)
            image_full_path = "%s%s" % (settings.IMAGE_URL, filename)

        bchar_array = base64.b64encode(str(self.char_array))
        self.db.messages.update({"message":image_full_path},
                                {"$set": {"result_map":bchar_array,
                                          "token":sender_token,
                                          "created_at":int(time.time())}},
                                          upsert=True)
        self.db.messages.update({"message":image_full_path},
                                {"$addToSet":{"accessors":sender_token}},
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
            self._generate_rgb(c)
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
