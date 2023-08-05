Introduction
============

The package detects, filters and sends requests to a logger. You can use ’collective.recipe.logger’ as a logger.

How it works
------------

What it does is:

1) Gets request which have not been published yet and sends them to the logger.

2) Adds an error information to logs and sends signal `open new storage` if any error happens.

As a result, we will have a bunch of files which will have the following structure::

  request

  request
    
  .......
    
  error info

I have to note that the package detects only server errors and  is intended to work with a production site.

Development
-----------

- Code repository: https://github.com/potar/collective.error.detector

- Please bootstrap the buildout and run the created ``bin/test`` to see if the tests still
  pass.  Please add tests if you add code.

- Questions and comments send to the Plone product-developers list or to
  potar: poburynnyitaras@gmail.com

Requirements
------------

* Plone 4.0
* Plone 4.1
* Plone 4.2
