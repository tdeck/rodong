rodong.py
=========

    Let us all turn out in the general offensive to hasten final victory
    in the revolutionary spirit of Paektu!

This Python module gives you programmatic access to the wisdom of the
Supreme Leader, and to the revolutionary Juche ideology of the DPRK!

Quick start
-----------

.. code:: shell

    pip install rodong

.. code:: python

    from rodong import RodongSinmun

    # Create a scraper
    scraper = RodongSinmun()

    # List the available sections
    print scraper.keys()

    # Get the first article in the "Supreme Leader's Activities" section
    # NOTE: This will be slow, as it builds the article index.
    #       subsequent accesses to the 'supreme_leader' list are cached
    article = scraper['supreme_leader'][0]

    # Print its title, content, and images
    print article.title
    print '=' * len(article.title)
    print article.text
    print
    print 'Images:'
    for i, image_url in enumerate(article.photos):
        print "\t[{0}]: {1}".format(i, image_url)

