What is this package
====================

The ``languagedet`` package implements language detection using stopwords and trigrams. It has three clases:

* ``languagedet.stopwords.StopWordsDetector``: detects language using stopword lists.
* ``languagedet.textcat.TextCatDetector``: uses the libexttexcat library for language detection.
* ``languagedet.mixed.MixedDetector``: uses StopWordsDetector and if it fails then use TextCatDetector.

Intallation
===========

This package depends on the libexttextcat library. To install it in Ubuntu::

    $ sudo apt-get install build-essential python-dev libexttextcat-dev

Now you can install using pip::

    $ pip install languagedet
    
Example
=======
::

    In [1]: from languagedet.mixed import MixedDetector
    
    In [2]: det = MixedDetector()
    
    In [3]: det.available
    Out[3]: 
    ['fr',
     'en',
     'de',
     'it',
     'da',
     'fi',
     'hu',
     'es',
     'ru',
     'nl',
     'pt',
     'no',
     'tr',
     'sv']
    
    In [4]: det('biblioteca para la detectar idioma')
    Out[4]: 'es'

Changelog
=========

Version 0.1.1
-------------

* Modified setup.py.
* Added a README.txt.
* Added a MANIFEST.in to include data files missing in version 0.1.
* Removed dependencies form cython and setuptools-cython.

Version 0.1
-----------

* Initial version.
* Support for language detectión using stopwords and the exttextcat library.
