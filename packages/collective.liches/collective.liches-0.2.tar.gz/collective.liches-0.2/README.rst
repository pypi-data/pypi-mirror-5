Introduction
============
Keeping the links in your site up to date is hard and unappreciated work.
Content editors need all the help and incentive they can get to do
this job. Liches_ tries to make this task a bit easier.


Installation
============

Liches
-------

You have to install a Liches_ linkchecker server for this product to work.
please follow the Liches_ installation instructions and make sure your
Liches_ server works before installing the plone product.


Plone
------

This addon can be installed has any other addons, please follow official
documentation_.

.. _documentation: http://plone.org/documentation/kb/installing-add-ons-quick-how-to

The short version is:
++++++++++++++++++++++

Add ``collective.liches`` to the list of eggs to install, e.g.

::

    [buildout]
    ...
    eggs =
        ...
        collective.liches

Re-run buildout, e.g. with

::

    $ ./bin/buildout

Restart Plone and activate the product in Plones Add-on configuration
section.


Usage
======

Configure the access to your Liches_ Linkchecker server and which content
types will be displayed on your link checker start page in the plone
control panel. The 'Secrect Key' is you Liches_ API Key and used to
update existing pages in the Liches server

.. image:: https://raw.github.com/collective/collective.liches/master/docs/liches-settings.png


Linkcheckers normally go through your site recursivly which
will result in many pages to be checked several times. The
linkchecker start pages tries to avoid this by giving the
linkchecker_ a page from which every relevant content item can be reached.
Append `@@linkchecker-startpage.html` to your siteroot to view this page.

.. image:: https://raw.github.com/collective/collective.liches/master/docs/linkchecker-startpage.png

The Liches portlet gives an overview how many pages with broken links
are present in the site or the current path.

.. image:: https://raw.github.com/collective/collective.liches/master/docs/liches-portlet.png

The links in the portlet take you to a page which gives you an overview
of the pages with broken links in the site or current path. Alternatively
append `@@linkchecker-brokenpages.html` to your site root or to any
folder(ish object) in your site.

.. image:: https://raw.github.com/collective/collective.liches/master/docs/broken-pages-in-site.png

All pages will show you (as long as you are able to edit it) which links
are broken. At the top you see a summary of the links and the result
of the linkcheck. Broken Links are highlighted and underlined in red.
After you corrected the links you may want to recheck the links in this
page. Press the 'Check Links' Button and wait for a few minutes for the
linkchecker_ to finish.

.. image:: https://raw.github.com/collective/collective.liches/master/docs/broken-links-in-page.png

Similar Products
================

You may also want to have a look at the competition.

gocept.linkchecker_  relies on a separate process gocept.lms_ to perform
external link-checking. It communicates with Plone via XML-RPC.

collective.linkcheck_ is an integrated solution, with a headless instance
processing items in the background.

Why yet another solution?
-------------------------

- I want my linkchecking to be independent from plone and to be
  able to monitor non plone sites with the same tool.
- Linkchecking is hard. The venerable linkchecker_ is a tried and tested
  tool that does this job good. It has lots of options to finetune the results
  to your needs e.g. to check the validity of HTLM and CSS.

.. _linkchecker: http://wummel.github.io/linkchecker/
.. _Liches: https://github.com/cleder/liches
.. _gocept.lms: https://pypi.python.org/pypi/gocept.lms/
.. _gocept.linkchecker: https://pypi.python.org/pypi/gocept.linkchecker/
.. _collective.linkcheck: https://pypi.python.org/pypi/collective.linkcheck/
