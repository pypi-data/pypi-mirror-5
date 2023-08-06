.. This is your project NEWS file which will contain the release notes.
.. Example: http://www.python.org/download/releases/2.6/NEWS.txt
.. The content of this file, along with README.rst, will appear in your
.. project's PyPI page.

News
====

0.6.1
-----

*Release date: 18-Sep-2013*

* New property "idNumber" that tries to identify a hash value or a
  serial number
* The usual bugfixes

0.6
---

*Release date: 16-Jul-2013*

* Better packaging: unittests and doc included in source tarball
* Fixes everywhere: unicode, release group detection, language detection, ...
* A few speed optimizations


0.5.4
-----

*Release date: 11-Feb-2013*

* guessit can be installed as a system wide script (thanks @dplarson)
* Enhanced logging facilities
* Fixes for episode number and country detection


0.5.3
-----

*Release date: 1-Nov-2012*

* GuessIt can now optionally act as a wrapper around the 'guess-language' python
  module, and thus provide detection of the natural language in which a body of
  text is written

* Lots of fixes everywhere, mostly for properties and release group detection


0.5.2
-----

*Release date: 2-Oct-2012*

* Much improved auto-detection of filetype
* Fixed some issues with the detection of release groups


0.5.1
-----

*Release date: 23-Sep-2012*

* now detects 'country' property; also detect 'year' property for series
* more patterns and bugfixes


0.5
---

*Release date: 29-Jul-2012*

* Python3 compatibility
* the usual assortment of bugfixes


0.4.2
-----

*Release date: 19-May-2012*

* added Language.tmdb language code property for TheMovieDB
* added ability to recognize list of episodes
* bugfixes for Language.__nonzero__ and episode regexps


0.4.1
-----

*Release date: 12-May-2012*

* bugfixes for unicode, paths on Windows, autodetection, and language issues


0.4
---

*Release date: 28-Apr-2012*

* much improved language detection, now also detect language variants
* supports more video filetypes (thanks to Rob McMullen)


0.3.1
-----

*Release date: 15-Mar-2012*

* fixed package installation from PyPI
* better imports for the transformations (thanks Diaoul!)
* some small language fixes

0.3
---

*Release date: 12-Mar-2012*

* fix to recognize 1080p format (thanks to Jonathan Lauwers)

0.3b2
-----

*Release date: 2-Mar-2012*

* fixed the package installation

0.3b1
-----

*Release date: 1-Mar-2012*

* refactored quite a bit, code is much cleaner now
* fixed quite a few tests
* re-vamped the documentation, wrote some more

0.2
---

*Release date: 27-May-2011*

* new parser/matcher completely replaced the old one
* quite a few more unittests and fixes


0.2b1
-----

*Release date: 20-May-2011*

* brand new parser/matcher that is much more flexible and powerful
* lots of cleaning and a bunch of unittests


0.1
---

*Release date: 10-May-2011*

* fixed a few minor issues & heuristics


0.1b2
-----

*Release date: 12-Mar-2011*

* Added PyPI trove classifiers
* fixed version number in setup.py


0.1b1
-----

*Release date: 12-Mar-2011*

* first pre-release version; imported from Smewt with a few enhancements already
  in there.
