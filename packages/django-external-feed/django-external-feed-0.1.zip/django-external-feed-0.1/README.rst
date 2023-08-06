django-external-feed
====================

Show content from an XML feed on your own site. This allows you to use
a commercial weblog service, yet you can still integrate the news
articles within your site.

.. contents::


Quick start
-----------

1. Add "externalfeed" to your INSTALLED_APPS setting like this::

      INSTALLED_APPS = (
          ...
          'externalfeed',
      )

2. Configure the feeds in your settings::

      FEED_SOURCES = (
          # (key, source, prefix to strip from the url)
          ('bbc',
           'http://feeds.bbci.co.uk/news/rss.xml',
           'http://www.bbc.co.uk/news'),
      )

   Note: not all external sources may allow you to embed their content
   like this.  You should check their terms of service.

   - The key is a text of your choosing that will end up in the url on
     your website.

   - The source is the url to an rss, atom or other syndication feed.
     We use feedparser_ to parse this.

   - The feed will have a url for each item.  The prefix is the part
     that we strip from this url.  The remainder of the url will end
     up in the url that makes this item available on your website.  If
     the url does not match the prefix, we take the part after the
     domain name.

3. Include the externalfeed URLconf in your project urls.py like this,
   or optionally roll your own::

      url(r'^externalnews/', include('externalfeed.urls')),


With the above settings, say the bbc rss feed has an item with this url::

    http://www.bbc.co.uk/news/uk-england-cumbria-23341015

This item will then be visible on your site at::

    <your-domain>/externalnews/bbc/uk-england-cumbria-23341015

When the item is no longer in the rss feed, the item is no longer
visible on your site.


Template tags
-------------

The url config will make some views with templates available, but you
can also roll your own.  In that case, the template tags will be
useful.  To make the template tags available, add this line in your
template::

    {% load feeder %}

These template tags are then available:

- ``single_feed``: show single feed

- ``feeds``: show all feeds.  Internally, this iterates over the feeds and
  uses the single_feed tag for each of them, passing its own arguments
  to that tag.

- ``feed_entry``: show single entry

- ``feed_entry_title``: show title of single entry

``feeds`` and ``single_feed`` take these optional arguments:
format_string (default: empty string, options: ``full`` and/or
``list``) and limit (default: 0, which means no limit).
``single_feed`` requires a key as first argument.

Show all feeds, with per entry only the title as a header::

    {% feeds %}

Show all feeds, with per entry also the contents::

    {% feeds "full" %}

Show all feeds, with entries in a simple list per feed::

    {% feeds "list" %}

Specifying ``full list`` is accepted, but the ``list`` wins then and
``full`` is ignored.  Note that at the moment the code simply checks
for the presence of the string ``full`` or ``list`` and not if the
words are separated by spaces.  A silly string like ``no fullist
ignored`` will match both ``full`` and ``list`` without complaining.

Show all feeds, with the default formatting, but limit to 2 entries per feed::

    {% feeds "" 2 %}

Show only the bbc feed::

    {% single_feed "bbc" %}

Show only the bbc feed in a simple list of the most recent 4 entries::

    {% single_feed "bbc" "list" 4 %}

The feed_entry and feed_entry_title tags both require a key and a path::

    {% feed_entry "bbc" "uk-england-cumbria-23341015" %}
    {% feed_entry_title "bbc" "uk-england-cumbria-23341015" %}


Compatibility
-------------

Tested with Django 1.4.3.  It is expected to work fine on Django 1.3
or higher.


.. Define links that are used above.

.. _feedparser: https://pypi.python.org/pypi/feedparser/
