======
rororo
======

.. image:: https://secure.travis-ci.org/playpauseandstop/rororo.png

Functional nano web-framework built on top of `WebOb <http://webob.org/>`_,
`routr <http://routr.readthedocs.com/>`_ and `Jinja2
<http://jinja.pocoo.org/>`_. Works on Python 2.6 and higher (Python 3
supported as well).

Requirements
============

* `Python <http://www.python.org/>`_ 2.6 or higher
* `WebOb`_ 1.2.3 or higher
* `routr`_ 0.7.1 or higher
* `Jinja2`_ 2.6 or higher

License
=======

``rororo`` library licensed under the terms of `BSD License
<https://github.com/playpauseandstop/rororo/blob/LICENSE>`_.

Installation
============

Sometimes in future ``rororo`` will added to PyPI, but for now you can install
it from master tarball, like::

    # pip install https://github.com/playpauseandstop/rororo/tarball/master#egg=rororo

For what reason?
================

Just to have little tool to fast creating WSGI applications. Little and easy
tool if you know what I mean. Prove?

::

    In [1]: from rororo import GET, create_app

    In [2]: from rororo.manager import runserver

    In [3]: view = lambda: 'Hello, world!'

    In [4]: app = create_app(routes=(GET('/', view), ))

    In [5]: runserver(app, autoreload=False)
    Starting server at http://0.0.0.0:8000/

More?
=====

Coming soon...
