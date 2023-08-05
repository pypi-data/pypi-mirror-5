======================================================================
 world -- Print mappings between country names and DNS country codes.
======================================================================

This script takes a list of top-level domain (TLD) codes and prints out where
in the world those top-level domains original from.  Domain codes can be any
ISO 3166 two-letter country code (ccTLD), such as ``it`` for ``Italy``, USA
top-level domains such as ``edu``, and any additional reserved or historical
global top-level domain code (gTLD) such as ``pro`` and ``su``.
Internationalized TLDs are not supported.

For example::

    $ world tz us
    tz originates from TANZANIA, UNITED REPUBLIC OF
    us originates from UNITED STATES

Reverse mappings are also supported.  In this case, the arguments are
interpreted as a Python regular expression, matched against the TLD
description.  The regular expression is matched case insensitively.

For example::

    $ world --reverse united
    Matches for "united":
      ae: UNITED ARAB EMIRATES
      gb: UNITED KINGDOM
      tz: TANZANIA, UNITED REPUBLIC OF
      uk: United Kingdom (common practice)
      um: UNITED STATES MINOR OUTLYING ISLANDS
      us: UNITED STATES

You can print out all the known mappings::

    $ world --all
    Country code top level domains:
        ad: ANDORRA
        ae: UNITED ARAB EMIRATES
        ...
    Additional top level domains:
        ac    : Ascension Island
        aero  : air-transport industry
        arpa  : Arpanet
        ...

There are other commands for downloading and regenerating the database, but
most users won't need this.  See ``world --help`` for details.


Author
======

Copyright (C) 2013 by Barry A. Warsaw
barry@python.org

Published under the terms of the GNU GPLv3.
