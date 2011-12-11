=========
lexicrypt
=========


What it is
==========

Token-based steganography.


Installation
============

sudo pip install -r requirements.txt


Message Flow
============

.. image:: http://dl.dropbox.com/u/1913694/lexicrypt-flow.png


Screenshot
==========

.. image:: https://img.skitch.com/20111120-fskaf7xhdu6rrs7c1jwkhasf77.jpg


Todo
====

* Allow removal of access tokens from message list
* Auto-generate image filenames
* Allow long messages to be converted to animated PNGs
* Move AES secret to be at author level and have a one-way hash
* If a visitor's api key matches one in the char_array's list, provide a
  browser notification that this image can be decrypted


Completed Items
===============

* Save self.char_array to a database, such that: author[messages: [message: accessors: [api_key_1, api_key_2, api_key_n]]]
* Allow them to decrypt by providing a link to the image


Additional Notes
================

* Api keys are tied to a user's email address
* Each user has an generated AES secret for their data. If this key is reset, all previous images will be regenerated