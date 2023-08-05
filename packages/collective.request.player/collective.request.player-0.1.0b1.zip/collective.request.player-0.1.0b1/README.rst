Introduction
============

The package replays a HTTP request.

How it works
------------

You have to do the following steps if you have a request storage:

1) Upload requests from a storage to Plone web form. The storage format has to be JSON or PICKLE.

2) Tick a request which you would like to replay.

3) Click 'Play'. Afterwards your request will be replayed by requests (python package).

If you don't have a request storage then you can set up a HTTP request manually through the Plone web form.

Development
-----------

- Code repository: https://github.com/potar/collective.request.player

- Please bootstrap the buildout and run the created ``bin/test`` to see if the tests still
  pass.  Please add tests if you add code.

- Questions and comments send to the Plone product-developers list or email
  potar: poburynnyitaras@gmail.com

Requirements
------------

* Plone 4.0
* Plone 4.1
* Plone 4.2
