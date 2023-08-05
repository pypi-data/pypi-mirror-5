saycloud: text to soundcloud
============================

Saycloud is a little python script (and some ancillary helpers) that glues together text-to-speech synthesisers with Soundcloud.

Currently supported are:

* OSX's 'say'
* Google Translate TTS

`You end up with something like this <https://soundcloud.com/cellols/test-foo-bar-baz#play>`_.

Installation
------------

.. code-block:: bash

  $ pip install saycloud

or

.. code-block:: bash

  $ easy_install saycloud

Usage
-----

.. code-block:: bash

  $ saycloud --help
  usage: saycloud [-h] [-e ENGINE] [-t TITLE] -s SAY [-v VOICE]

  Saycloud - text to Soundcloud.

  optional arguments:
    -h, --help            show this help message and exit
    -e ENGINE, --engine ENGINE
                          The language engine to use for text to speech (default
                          is "say").
    -t TITLE, --title TITLE
                          Track title (on Soundcloud)
    -s SAY, --say SAY     Words to say.
    -v VOICE, --voice VOICE
                          Voice to use. Get a list for say on OSX: say -v ? or
                          for Google Tranlsate:
                          https://developers.google.com/translate/v2/using_rest
                          #language-params
Example
-------

An entertaining little example to get you going:

.. code-block:: bash

  $ saycloud -t "Test Foo Bar Baz" -v "Cellos" -s "Foo foo foo foo foo foo bar foo foo bar bar bar baz foo foo foo foo foo foo foo bar foo bar foo bar baz"


Which will run something like this the first time around:

.. code-block:: bash

  Incorrect username/password
  username: cellols
  Password:
  Do you want to store your Soundcloud username and password at
  ~/.saycloud so you don't have to enter them in future? (y/n) y
  https://soundcloud.com/cellols/test-foo-bar-baz

Further reading
---------------

Google Translate has many languages/voices it can mangle your text with, some of which may just produce noise or otherwise not work.

You can see a `full list of the language codes here <https://developers.google.com/translate/v2/using_rest#language-params>`_.

By default, `en` is used.
