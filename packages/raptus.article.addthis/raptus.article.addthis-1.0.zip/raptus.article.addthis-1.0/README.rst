.. contents::

Introduction
============


Shows addthis_ links below the article's text.

.. _addthis: http://www.addthis.com

The code will be wrapped in ``div#raptus-article-addthis`` for including the
addthis code with diazo.


If the component is activated (and ``addthis_active`` is set to ``True`` in the
`raptus properties` (see Configuration_) the addthis buttons are shown below
the text.





Configuration
=============


First register at addthis_ and get the
`most recent sharing code from the addthis homepage`_ ..


.. _:https://www.addthis.com/get/sharing



 Configuration options can be found in
``portal_properties/raptus_article``::


addthis_active
  boolean, if true - addthis buttons are shown below articles with the addthis
  component activated

addthis_code
    html code and javascript as obtained from addthis



Why this package?
=================


collective.addthis does not work on per-content-basis. you either have addthis
buttons for all document or none at all.

zest.social is quite similar. however, it requires to uses z3c.jbot to use your
own addthis account.

In addition this package integrates nicely in portals
using raptus.article (since it's a component)



TODOS
=====

none, atm


Dependencies
============

* raptus.article.core



