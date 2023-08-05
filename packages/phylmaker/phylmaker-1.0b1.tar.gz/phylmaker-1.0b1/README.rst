Phylmaker
=========

Phylmaker is a modern Python library for interacting with the XML API
of FileMaker Servers.


Installation
------------

Phylmaker is available in PyPI; the `Python Package Index`_, so:

    $ pip install phylmaker

Or for the very latest development version, you can get it from BitBucket:

    $ pip install hg+https://bitbucket.org/Raumkraut/phylmaker#egg=phylmaker

Requirements:

* Python >= 2.6
* Requests_ >= 1.0


Usage
-----

Quickstart example:

    >>> import phylmaker
    >>> srv = phylmaker.FMServer('fm.example.com', 'username', 'passphrase')
    >>> srv.get_dbs()
    [u'foo', u'bar', u'baz']
    >>> srv.get_layouts('foo')
    {u'spam': <phylmaker.server.FMLayout foo/spam (fm.example.com)>}
    >>> layout = srv.get_layout(db='bar', layout='eggs')
    >>> layout
    <phylmaker.server.FMLayout bar/eggs (fm.example.com)>
    >>> results = layout.find(canhas='*burger').execute()
    >>> list(res['canhas'] for res in results)
    [u'Hamburger', u'Cheeseburger', u'Tofuburger']

For everything else, ``help()`` and ``dir()`` are your friends!


License
-------

Phylmaker is licensed under the terms of the `X11/MIT license`_:

    Copyright (c) 2012, Mel Collins <mel@raumkraut.net>
    
    Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby granted, provided that the above copyright notice and this permission notice appear in all copies.
    
    THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.


.. _`Python Package Index`: https://pypi.python.org/pypi
.. _`Requests`: http://docs.python-requests.org/en/latest/
.. _`X11/MIT License`: http://opensource.org/licenses/MIT
