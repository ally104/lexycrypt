=========
lexicrypt
=========


Beta Site
=========

http://lexicrypt.com


What it is
==========

Token-based message distribution using encryption.


Installation
============

Install MongoDB or set up an account at http://mongohq.com

::

    $ sudo pip install -r requirements.txt
    $ mkdir lexicrypt/tmp
    $ cp lexicrypt/setings.py-local lexicrypt/settings.py

Then edit ``lexicrypt/settings.py``.


Message Flow
============

.. image:: http://dl.dropbox.com/u/1913694/lexicrypt-flow.png


Screenshots
===========

.. image:: http://dl.dropbox.com/u/1913694/lexicrypt_sample_1.png

.. image:: http://dl.dropbox.com/u/1913694/lexicrypt_sample_2.png

.. image:: http://dl.dropbox.com/u/1913694/lexicrypt_sample_3.png

.. image:: http://dl.dropbox.com/u/1913694/lexicrypt_sample_4.png


Todo
====

* Allow regeneration of api keys
* Allow long messages to be converted to parts


Completed Items
===============

* Auto-generate image filenames
* If a visitor's api key matches one in the char_array's list, provide
  a browser notification that this image can be decrypted
* Save self.char_array to a database, such that: author[messages:
  [message: accessors: [api_key_1, api_key_2, api_key_n]]]
* Allow them to decrypt by providing a link to the image
* Allow removal of access tokens from message list


Running the Tests
=================

In the top level of the project, run the following::

    $ python -m unittest lexicrypt.tests.test


Additional Notes
================

* Api keys are tied to a user's email address
* Each user has an generated AES secret for their data. If this key is
  reset, all previous images will be regenerated
