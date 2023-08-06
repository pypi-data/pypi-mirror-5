scrapy-redirect restricts authorized HTTP redirections to the website start_urls

Why?
----

If the `Scrapy <http://scrapy.org/>`_ ``REDIRECT_ENABLED`` config key is set to ``False`` and a request to the homepage of the crawled website returns a `3XX status code <https://en.wikipedia.org/wiki/List_of_HTTP_status_codes#3xx_Redirection>`_, the crawl will stop immediatly, as the redirection will not be followed.

scrapy-redirect will force Scrapy to tolerate redirections coming from the ``start_urls`` urls, in the case  where ``REDIRECT_ENABLED = False``, to avoid this particular problem.

Installation
------------

.. code-block:: bash

    $ pip install scrapy-redirect


Configuration
--------------

Install scrapy-redirect in your Scrapy middlewares by adding the following key/value pair in the ``SPIDER_MIDDLEWARES`` settings key (in ``settings.py``):

.. code-block:: python

    SPIDER_MIDDLEWARES = {
        ...
        'scrapyredirect.HomepageRedirectMiddleware': 575,
        ...
    }

Note that it is important for the middleware order value to be inferior to 600 (the `default value <http://doc.scrapy.org/en/0.16/topics/settings.html#downloader-middlewares-base>`_  of the ``'scrapy.contrib.downloadermiddleware.redirect.RedirectMiddleware'`` middleware), as it must be executed before Scrapy blocks the redirection.

NB: if ``REDIRECT_ENABLED = True``, scrapy-redirect does nothing.

License
-------

scrapy-redirect is published under the MIT License.