Introduction
============
.. image:: https://secure.travis-ci.org/bsuttor/bobtemplates.bsuttor.png
     :target: http://travis-ci.org/bsuttor/bobtemplates.bsuttor

``bobtemplates.bsuttor`` is a `mr.bob`_ templates to generate strucutre packages for Plone projects. 

At the moment, there is only one template for a empty `Plone`_ add-on

Hot to create a Plone add-on package
------------------------------------

You have to install ``mr.bob`` and ``bobtemplates.bsuttor`` eggs. Then you can run `mrbob`::

    $ pip install mr.bob
    $ pip install bobtemplates.bsuttor
    $ mrbob -O collective.foo bobtemplates:plone

You have to answer some questions::

    Welcome to mr.bob interactive mode. Before we generate directory structure,
    some questions need to be answered.

    Answer with a question mark to display help.
    Value in square brackets at the end of the questions present default value
    if there is no answer.


    --> Namespace of the package: collective
    [...]

Now you can install your add on::

    $ cd collective.foo
    $ make install

Finally you can lauch test::

    $ bin/test

Or starting Plone::

    $ bin/instance fg

Go with your browser to ``http://localhost:8080/Plone``, and you can see your site with your module installed

It's time to customize it ;-), see `Plone developer`_ help

Other example
-------------

You can see other example of bobtempaltes which are inspired me

* https://github.com/iElectric/bobtemplates.ielectric
* https://github.com/Kotti/bobtemplates.kotti
* https://github.com/niteoweb/bobtemplates.niteoweb

.. _mr.bob: http://mrbob.readthedocs.org/en/latest/
.. _Plone: http://plone.org
.. _Plone developer: http://developer.plone.org
