=========
lexicrypt
=========


What it is
==========

Token-based message distribution using encryption and steganography.


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

* Allow regeneration of api keys
* Allow long messages to be converted to animated PNGs


Completed Items
===============

* Auto-generate image filenames
* If a visitor's api key matches one in the char_array's list, provide a
  browser notification that this image can be decrypted
* Save self.char_array to a database, such that: author[messages: 
  [message: accessors: [api_key_1, api_key_2, api_key_n]]]
* Allow them to decrypt by providing a link to the image
* Allow removal of access tokens from message list


Running the Tests
=================

In the top level of the project, run the following:

python -m unittest lexicrypt.tests.test


Additional Notes
================

* Api keys are tied to a user's email address
* Each user has an generated AES secret for their data. If this key is reset, all previous images will be regenerated
