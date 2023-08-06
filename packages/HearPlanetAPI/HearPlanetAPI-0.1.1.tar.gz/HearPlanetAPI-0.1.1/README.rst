About
=====

This is the HearPlanet supported Python driver for HearPlanet’s public
API.

This API supports queries to HearPlanet’s database of Points of
Interest, Articles, Images and Audio files.

If you need additional support, please visit http://www.hearplanet.com/

Overview
========

Setup
-----

The easiest way to get started with the driver is to install it from the
Python Package Index.

::

    pip install HearPlanetAPI

First you need to obtain API access credentials from HearPlanet.

Create a configuration file containing your credentials, by copying and
customizing hearplanet.cfg.example to one, or both, of the following:

1. /etc/hearplanet.cfg ### Site-wide
2. ~/.hearplanet.cfg ### Individual

To use the driver in a Python program, just …

::

    from hearplanet import HearPlanet  
    api = HearPlanet()

example.py is provided with the driver as a reference.

Dependencies
------------

Minimum Python version 2.5.

`Requests`_

Basic Design
------------

The driver allows you to access the HearPlanet API, sending requests and
getting data back.

One thing to be aware of is the behavior of the query modifier
functions. These return new query instances, so base queries can be set
up and then modified in different ways to produce new queries.

You specify the table (type of object) you want to search for, the
search terms, and various filters and modifiers. The search is executed
when you access the response object.

Tables
------

Many of the HearPlanet database tables can be accessed. However,
generally if you are only making requests, you will only need to be
accessing the “article” and/or “poi” tables. The general layout looks
something like this:

::

    table('poi')
    table('article')
        fetch({id}, objects={'object'}, size={'image_size_code'})
        search()
            term('A Query Term')
            point({'lat':'37.0', 'lng':'-122.5'})
            location('123 Address St., Anytown')
            filters({'key':'value'})
        featured()

First you would select the table (poi or article). If you already know
the unique identifier of the poi or article, you can use fetch(). If you
would like to get the “featured” articles, then just use featured().
Otherwise, use search() plus one or more of term(), point() and
location(). Finally, you can add filters to further refine your search.

Other tables of interest might be “langugages” and “categories.” For a
complete list, consult the `API documentation`_.

Search Requests
---------------

Searches for POI’s and Articles can be performed based on location or
query term.

Location searches return POI’s and Articles near a point – either a
latitude/longitude or an address (or other geocodable location). If you
give both point() and location(), objects near location will be used,
and distances to that location will be calculated from point. Examples:

::

    point({'lat':'37.0', 'lng':'-122.5'})
    location('123 Address St., Anytown')

Query Term searches do a full-text search in the title of the POI or
Article.

::

    term('Pizza')

In combination:

::

    # Search for POI's with "Pizza" in their title located in
    # Chicago, calculating distances from the given point.
    req = api.table('poi').search()
    req = req.term('Pizza').location('Chicago, IL')
    req = req.point({'lat':'37.0', 'lng':'-122.5'})

Fetch a particular POI or Article if you have its id:

::

    req = api.table('article').fetch(999999)

If you only want some of the objects associated with an article, you can
request them specifically. For example, if an article has email
addresses associated with it:

::

    req = api.table('article').fetch(999999, 'emails')

Images take an optional ‘size’ parameter, for example ‘T’ for thumbnail:

::

    req = api.table('article').fetch(999999, 'images', 'T')

The full list of article objects is:

-  addresses
-  audio
-  categories
-  details
-  emails
-  images
-  phones
-  rating\_average
-  ratings
-  reviews
-  sections
-  sections\_f
-  tags
-  websites

Get featured Articles :

::

    req = api.table('article').featured()

Search Request Filters
----------------------

Filters can be applied to the searches:

::

    req = req.filters({'ch':'hearplanet'})
    req = req.filters({'lang':'fr'})
    req = req.filters({'bbox':'(37.3,-122.8)(37.6,-120.0)'})
    req = req.filters({'radius':15'}) # search radius in kilometers

Request modifiers
-----------------

Request modifiers are used for paging results, selecting the text format
and the amount of data returned.

You can either use limit() and offset() together, or just use page().
The default values for offset and limit are 0 and 10, respectively. If
you use page(), just specify an integer page number from 1 to N. The
default page length is 10.

::

    limit(max_rows)
    offset(offset)
    page(page_num, limit=DEFAULT_LIMIT)
    format(format) # ('HTML', 'HTML-RAW', 'XHTML', 'PLAIN', 'AS-IS')
    depth(depth) # ('min', 'poi', 'article', 'section',
                    'section_text', 'all',)

-  The format modifiers change the formatting of the section text.
   Normally this is set on the backend and you don’t have to worry about
   it. However, if necessary you can override it.

-  The depth modifiers change the amount of information that is
   returned. That’s primarily for performance enhancement, when
   accessing the API over a slow network. For example, make a shallow
   initial search using the poi.json endpoint at depth ‘poi’ to get a
   list of POI’s and their Articles. Then the full Article can be
   selected by the user, and a second request made for just that Article
   using fetch().

First do a shallow search of POI’s that have “Pizza” in their title
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    poi_list = api.table('poi').search().term('Pizza').depth('poi').page(1).objects()

Get the id of the first Article in the first POI
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    first_poi = poi_list[0]
    first_article_id = first_poi.articles[0].id
    print first_poi

Now get all the data related to that Article
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    article = api.table('article').fetch(first_article_id).objects()
    print article

Examples
--------

Create an API query object
~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    api = HearPlanet()

Specify a search of the POI table
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    req = api.table('poi').search()

Add a query term, and search origin
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    req = req.term('Golden Gate')
    req = req.location('San Francisco, CA')

Add a filter: only return articles in the Wikipedia channel
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    req = req.filters({'ch':'wikipedia'})

Ask for only the first page (default is the first 10 objects)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    req = req.page(1)

Get the return value as data or objects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    objects = req.objects()  

Do something with the objects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    for poi in objects:
        print poi.title

Or, you can chain the requests all together
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    pois = api.table('poi').search().term('Golden Gate').location('San Francisco, CA').filters({'ch':'wikipedia'}).page(1).objects()

Unit Tests
----------

Unit Tests are provided to ensure the driver is functioning as expected.
The unit tests also serve as examples of various API requests.

You can run the Unit Tests in test\_hearplanet.py like this:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    python test_hearplanet.py

URL Encoding
------------

The Python driver handles URL encoding, therefore all parameters passed
to the driver should be in their un-encoded form.



.. _Requests: http://docs.python-requests.org/en/latest/
.. _API documentation: http://prod.hearplanet.com/api/2.0/documentation/
