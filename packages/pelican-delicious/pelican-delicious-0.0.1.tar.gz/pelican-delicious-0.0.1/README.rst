===========================
Pelican Delicious bookmarks
===========================

.. image:: https://travis-ci.org/2xyo/pelican-delicious.png?branch=master
    :target: https://travis-ci.org/2xyo/pelican-delicious
.. image:: https://coveralls.io/repos/2xyo/pelican-delicious/badge.png?branch=master 
    :target: https://coveralls.io/r/2xyo/pelican-delicious?branch=master

Pelican Delicious Bookmarks is a library to make it easy to add your Delicious bookmarks in your Pelican_ blogs.

Installation
------------

To install pelican-delicious, simply:

.. code-block:: bash

    $ pip install pelican-delicious

Then add a bit of code to your blog configuration:

.. code-block:: python

    PLUGINS = [
        # ...
        'pelican_delicious',
        # ...
    ]

Usage
-----

In your articles, just add lines to your posts that look like:

.. code-block:: html

    [delicious:tags=tag1 tage2]

This will tell the plugin to insert links withs tag1 and tag2 into your post. The resulting HTML will look like:

.. code-block:: html

    <div class ="delicious">
        <dl>
            <dt>Title</dt>
            <dd>The Titile of the link</dd>

            <dt>Description</dt>
            <dd>The Description</dd>

            <dt>URL</dt>
            <dd><a href="http://www.example.com"/></dd>
        </dl>
    </div>



Settings
--------
Create the file pelican-creds.py with your credentials :

.. code-block:: python

    DELICIOUS_USERNAME = 'Your Delicious username'
    DELICIOUS_PASSWORD = 'Your Delicious password'


Import this config in your pelicanconf.py :

.. code-block:: python

    import pelican-delicious
    from pelican-delicious import *

You can also modify the default template:

.. code-block:: html

    DELICIOUS_TEMPLATE = """
         <div class="delicious">
        {% for bookmark in bookmarks %}
            <dl>
                <dt>Title</dt>
                <dd>{{ bookmark.title }}</dd>
                {% if bookmark.description %}
                <dt>Description</dt>
                <dd>{{ bookmark.description }}</dd>
                {% endif %}
                <dt>URL</dt>
                <dd><a href="{{ bookmark.url }}"/></dd>
            </dl>
        {% endfor %}
        </div>"""


Don't forget to add pelican-creds.py to your .gitignore!

License
-------

Uses the `BEER-WARE`_ license.


.. _Pelican: http://blog.getpelican.com/
.. _BEER-WARE: http://people.freebsd.org/~phk/
.. _pelican-gist: https://github.com/streeter/pelican-gist

