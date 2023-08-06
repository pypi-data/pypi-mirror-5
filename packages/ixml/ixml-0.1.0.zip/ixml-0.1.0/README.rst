=================================================
iXML - A simple iterative event-driven XML parser
=================================================

.. image:: https://secure.travis-ci.org/YAmikep/ixml.png
    :target: https://travis-ci.org/YAmikep/ixml

.. image:: https://coveralls.io/repos/YAmikep/ixml/badge.png
   :target: https://coveralls.io/r/YAmikep/ixml  

.. image:: https://pypip.in/v/ixml/badge.png
    :target: https://crate.io/packages/ixml/

.. image:: https://pypip.in/d/ixml/badge.png
    :target: https://crate.io/packages/ixml/


iXML is an iterative event-driven XML parser with a standard Python iterator interface.



Docs
----

.. http://ixml.readthedocs.org/en/latest/



Install
-------

From PyPI (stable)::

    pip install ixml

From Github (unstable)::

    pip install git+git://github.com/YAmikep/ixml.git#egg=ixml


iXML currently requires the `lxml <http://lxml.de/>`_ library because there is no fallback backend based on the standard library yet.


Main API
---------

- ``ixml.parse(data)``: iterator returning parsing events.

- ``ixml.items(data, path, builder_klass=DictObjectBuilder)``: iterator returning Python objects found under a specified path.

Notes:

- ``data`` must be a file like object.

- The Python objects yielded by ``ixml.items`` are constructed from the parsing events by an ``ObjectBuilder`` (``DictObjectBuilder`` by default). Please make your own if you wish as long as it implements the ``ObjectBuilder`` interface (see ``ixml.builders.interface``).

- Top-level ``ixml`` module tries to automatically find and import a suitable parsing backend. You can also explicitly import a required backend from ``ixml.backends``.



Usage and examples
------------------

All examples will be using this XML document:

.. code:: python

    >>> XML = '''<?xml version="1.0" encoding="utf-8"?>
    <cities>
        <city name="Paris">
            <country>France</country>
            <language>French</language>
            <attractions>
                <monument>Eiffel Tower</monument>
                <monument>Triumphal Arch</monument>
                <museum>Louvre Museum</museum>
                <museum>Quai Branly Museum</museum>
            </attractions>          
        </city>
        <city name="Dallas">
            <country>USA</country>
            <language>English</language>
            <attractions>
                <monument>Bank America Plaza</monument>
                <monument>Dallas Theatre Center</monument>
                <museum>Dallas Museum of Art</museum>
                <museum>Old Red Museum</museum>
            </attractions>          
        </city> 
    </cities>'''


- **ixml.parse**

Using the ``parse`` function, you can react on individual events:

.. code:: python

    >>> import ixml
    >>> from StringIO import StringIO
    
    # The parse function takes a file like object
    >>> data = StringIO(XML)

    # Extract only the languages and the countries
    >>> languages, countries = set(), set()
    >>> for path, event, value in ixml.parse(data):
    ...     if path == 'cities.city.language':
    ...         languages.add(value)
    ...     elif path == 'cities.city.country':
    ...         countries.add(value)
    >>> print languages, countries
    set(['French', 'English']) set(['USA', 'France'])


Below are all the parsing events from ``parse``:

.. code:: python

        ('cities', u'start', None)
        ('cities.city', u'start', None)
        ('cities.city.@name', 'data', 'Paris')
        ('cities.city.country', 'data', 'France')
        ('cities.city.language', 'data', 'French')
        ('cities.city.attractions', u'start', None)
        ('cities.city.attractions.monument', 'data', 'Eiffel Tower')
        ('cities.city.attractions.monument', 'data', 'Triumphal Arch')
        ('cities.city.attractions.museum', 'data', 'Louvre Museum')
        ('cities.city.attractions.museum', 'data', 'Quai Branly Museum')
        ('cities.city.attractions', u'end', None)
        ('cities.city', u'end', None)
        ('cities.city', u'start', None)
        ('cities.city.@name', 'data', 'Dallas')
        ('cities.city.country', 'data', 'USA')
        ('cities.city.language', 'data', 'English')
        ('cities.city.attractions', u'start', None)
        ('cities.city.attractions.monument', 'data', 'Bank America Plaza')
        ('cities.city.attractions.monument', 'data', 'Dallas Theatre Center')
        ('cities.city.attractions.museum', 'data', 'Dallas Museum of Art')
        ('cities.city.attractions.museum', 'data', 'Old Red Museum')
        ('cities.city.attractions', u'end', None)
        ('cities.city', u'end', None)
        ('cities', u'end', None)


- **ixml.items**

Another usage is having iXML yields native Python objects for a specific path with ``items``:

.. code:: python

    >>> import ixml
    >>> from StringIO import StringIO
    
    # The items function takes a file like object
    >>> data = StringIO(XML)

    >>> for city in ixml.items(data, 'cities.city'):
    ...     do_something_with(city)


Below are the two "city" Python objects created. They are constructed as a dict by default. 
You can change this behavior by providing another builder class to the ``items`` function.

.. code:: python

    {   
        'country': 'France', 
        '@name': 'Paris', 
        'language': 'French', 
        'attractions': {
            'museum': ['Louvre Museum', 'Quai Branly Museum'],
            'monument': ['Eiffel Tower', 'Triumphal Arch']
        }
    }
    {
        'country': 'USA',
        '@name': 'Dallas',
        'language': 'English',
        'attractions': {
            'museum': ['Dallas Museum of Art', 'Old Red Museum'], 
            'monument': ['Bank America Plaza', 'Dallas Theatre Center']
        }
    }



Parsing events
--------------

Parsing events contain the XML tree context (path), an event and a value::

    (path, event, value)


1. **The tree context (or path)**

It is a simplified path format that:

- uses dots to define different levels
- uses namespace prefixes in the tag name
- ignores default namespaces (handled automatically behind the scene)
- uses @ for attributes

Examples:

- rss.channel.item
- rss.channel.item.@myAttr
- rss.channel.ns1:item.title


2. **The events**

- "start" and "end" for containers:

.. code:: python

    <rss>   # => ('rss', 'start', None)
        <...>
    </rss>  # => ('rss', 'end', None)


- "data" for leaves and attributes:

.. code:: python

    <rss>   
        <title myAttr="Test">Some text</title>  # => ('rss.title', 'data', 'Some text'), ('rss.title.@myAttr', 'data', 'Test')
    </rss>


3. **The value**

If there is a value, it will always be a string, None otherwise.
There is currently no automatic conversion feature (to int, etc).


Backends
--------

iXML can provide several implementation of the parsing by using backends located in ixml/backends:

- ``lxmliterparse``: wrapper around the well known `iterparse LXML <http://lxml.de/parsing.html#iterparse-and-iterwalk>`_ function.

You can import a specific backend and use it in the same way as the top level library:

.. code:: python

    >>> import ixml.backends.lxmliterparse as ixml
    >>> for path, event, value in ixml.parse(...):
    ...     # ... 

Importing the top level library as ``import ixml`` tries to import all backends in order.

iXML currently requires the `lxml <http://lxml.de/>`_ library because there is no fallback backend based on the standard library yet.



ObjectBuilder
------------
The ``items`` function uses an ObjectBuilder to build an object while parsing the data.

The events are passed into the ``event`` function of the builder that accepts three parameters: path, event type and value.
The object being built is available at any time from the ``value`` attribute.

You can make your own builder as long as it implements the ObjectBuilder interface (see ixml/builders/interface).



Contribute
----------

Clone and install testing dependencies::

    $ python setup.py develop 
    $ pip install -r requirements_tests.txt

Ensure tests pass::

    $ ./scripts/runtests.sh

Or using tox::

    $ tox
