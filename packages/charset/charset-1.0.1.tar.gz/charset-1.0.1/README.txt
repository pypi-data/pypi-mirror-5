What is this package
====================

The ``charset`` detects character encodings using the ``Universal Charset Detector`` implemented
by Mozilla. If the text cannot be converted with the charset detected using the ``Universal Charset
Detector`` then it uses the ``chardet`` package.

Intallation
===========

You can install using pip::

    $ pip install charset
    
Example
=======
::

    In [1]: from charset import Detector, text_to_unicode, text_to_utf8
    
    In [2]: det = Detector()
    
    In [3]: input_text = open('input.txt').read()
    
    In [3]: text1 = text_to_unicode(input_text)
    
    In [4]: text2 = text_to_utf8(input_text)

Changelog
=========

Version 1.0.1 (2013-11-20)
--------------------------

* Modified setup.py.
* Added a README.txt.
* Added a MANIFEST.in to include data files missing in version 1.0.
* Removed dependencies form cython and setuptools-cython.
* Add dependency of chardet.

Version 1.0 (2013-04-21)
------------------------

* Initial version.
* Support for character encoding detection.
