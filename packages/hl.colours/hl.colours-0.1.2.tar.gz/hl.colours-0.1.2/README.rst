hl.colours - colors for terminal output
=======================================

**hl.colours** add colours to terminal output.


Installation
------------

**Automatic installation**::

    pip install hl.colours

HtmlNode is listed in `PyPI <http://pypi.python.org/pypi/hl.colours>`_ and
can be installed with ``pip`` or ``easy_install``.

**Manual installation**: Download the latest source from `PyPI
<http://pypi.python.org/pypi/hl.colours>`_.

.. parsed-literal::

    tar xvzf hl.colours-$VERSION.tar.gz
    cd hl.colours-$VERSION
    sudo python setup.py install

The `hl.colours` source code is `hosted on GitHub
<https://github.com/hllau/hl.colours>`_.



Usage Example
-------------

Usage::

    import hl.colours as k

    for color in ['red', 'yellow', 'bblue', 'byellow']:
        print getattr(k, color)(color)

    print yellow('This is yellow.')
    print bred('This is stronger red.')

