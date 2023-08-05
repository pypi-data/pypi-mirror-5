.. sql-helper documentation master file, created by
   sphinx-quickstart on Thu Feb 14 22:47:45 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

MoSQL --- More than SQL
=======================

It lets you use the common Python's data structures to build SQLs, and provides a
convenient model of result set.

The talk, "MoSQL: More than SQL, but Less than ORM", at PyCon TW 2013:

.. raw:: html

    <div style="width: 600px">
        <script async class="speakerdeck-embed"
        data-id="5c9f3200a72b0130a3946ae3c3cecfe8" data-ratio="1.33507170795306"
        src="//speakerdeck.com/assets/embed.js"></script>
    </div>

The main features:

1. Easy-to-learn --- Everything is just plain data structure or SQL keyword. See
   `The SQL Builders`_.
2. Convenient    --- It makes result set more easy to use. See `The Model of
   Result Set`_.
3. Secure        --- It prevents the SQL injection from both identifier and
   value.
4. Faster        --- It just builds the SQLs from Python's data structure and
   then send it via the connector.

It is just "More than SQL".

.. raw:: html

    <div id="fb-root"></div>
    <script>(function(d, s, id) {
      var js, fjs = d.getElementsByTagName(s)[0];
      if (d.getElementById(id)) return;
      js = d.createElement(s); js.id = id;
      js.src = "//connect.facebook.net/zh_TW/all.js#xfbml=1";
      fjs.parentNode.insertBefore(js, fjs);
    }(document, 'script', 'facebook-jssdk'));</script>


    <style>
    #social-btns div {
        float: left;
    }
    #social-btns:after {
        content: ".";
        display: block;
        font-size: 0;
        clear: both;
    }
    </style>

    <div id='social-btns'>
        <div>
            <iframe src="http://ghbtns.com/github-btn.html?user=moskytw&repo=mosql&type=watch&count=true" allowtransparency="true" frameborder="0" scrolling="0" width="85" height="20"></iframe>
        </div>

        <div>
            <div class="fb-like" data-href="http://mosql.mosky.tw" data-send="true" data-layout="button_count" data-width="450" data-show-faces="true"></div>
        </div>
    </div>

NOTE: The versions after v0.2 is a new branch and it does **not** provide backward-compatibility for
v0.1.x.

The SQL Builders
----------------

::

    >>> from mosql import build
    >>> build.select('author', {'email like': '%mosky%@%'})
    SELECT * FROM "author" WHERE "email" LIKE '%mosky%@%'

It is very easy to build a query by Python's data structures and
:mod:`mosql.build`.

.. seealso ::

    There is more explanation of the builders --- :class:`mosql.build`.

It also provides :class:`mosql.result.Model` for result set, and you can use the
same way to make queries to database.

The Model of Result Set
-----------------------

Here is a SQL and the result set:

::

    mosky=> select * from detail where person_id in ('mosky', 'andy') order by person_id, key;
     detail_id | person_id |   key   |           val            
    -----------+-----------+---------+--------------------------
             5 | andy      | email   | andy@gmail.com
             3 | mosky     | address | It is my first address.
             4 | mosky     | address | It is my second address.
             1 | mosky     | email   | mosky.tw@gmail.com
             2 | mosky     | email   | mosky.liu@pinkoi.com
            10 | mosky     | email   | mosky@ubuntu-tw.org
    (6 rows)

Then, use the model configured (the module, ``detail``, is in the `examples
<https://github.com/moskytw/mosql/tree/dev/examples>`_) to do so:

::

    >>> from detail import Detail
    >>> for detail in Detail.arrange({'person_id': ('mosky', 'andy')}):
    ...     print detail
    ... 
    {'detail_id': [5],
     'key': 'email',
     'person_id': 'andy',
     'val': ['andy@gmail.com']}
    {'detail_id': [3, 4],
     'key': 'address',
     'person_id': 'mosky',
     'val': ['It is my first address.', 'It is my second address.']}
    {'detail_id': [1, 2, 10],
     'key': 'email',
     'person_id': 'mosky',
     'val': ['mosky.tw@gmail.com', 'mosky.liu@pinkoi.com', 'mosky@ubuntu-tw.org']}

Here I use :meth:`~mosql.result.Model.arrange` for taking advantages from the
model configured, so the result sets are grouped into three model instances, but
the plain methods, such as :meth:`~mosql.result.Model.select`, are also
available.

It converts the result set to column-oriented models, and the column can be
squashed. The non-list value above is just the squashed column. See
:class:`mosql.result` for more information.

.. seealso ::

    There is more explanation of the model --- :class:`mosql.result`.

Installation
------------

It is easy to install MoSQL with pip:

::

    $ sudo pip install mosql

Or clone the source code from `Github <https://github.com/moskytw/mosql>`_:

::

    $ git clone git://github.com/moskytw/mosql.git

The Documentions
================

.. toctree::
    :maxdepth: 2

    result.rst
    builders.rst
    escape.rst
    changes.rst

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
