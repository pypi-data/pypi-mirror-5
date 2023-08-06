============
infrae.uwsgi
============

**Buildout recipe downloading, compiling and configuring uWSGI.**

Creates a ``bin/`` uWSGI_ executable and ``parts`` XML configuration
file with which you can easily launch Buildout sandboxed uWSGI_
processes.

This recipe is a fork of shaunsephton.recipe.uwsgi, in order to update
it to work with recent versions of Buildout and UWSGI. All credits
goes to its original authors.

.. contents::

Usage
=====

Add a part to your ``buildout.cfg`` like so::

    [buildout]
    parts=uwsgi

    [uwsgi]
    recipe=infrae.uwsgi

Running the buildout will download and compile uWSGI_ and add an
executable with the same name as your part in the ``bin/``
directory. In this case ``bin/uwsgi``. It will also create a
``uwsgi.xml`` configuration file in a ``parts`` directory with the
same name as your part. In this case ``bin/uwsgi/uwsgi.xml``.

This allows you to start a uWSGI_ process configured by the generated
XML file, i.e.::

    $ ./bin/uwsgi --xml parts/uwsgi/uwsgi.xml

The generated XML configuration includes ``pythonpath`` directives
referencing the various Python eggs installed by Buildout allowing
uWSGI_ to utilize them.

You can specify any and all additional uWSGI_ configuration options as
additional options of the Buildout part. For instance to specify a
socket and module and to enable the master process add ``socket``,
``module`` and ``master`` options to the buildout part, i.e.::

    [buildout]
    parts=uwsgi

    [uwsgi]
    recipe=infrae.uwsgi
    socket=127.0.0.1:7001
    module=my_uwsgi_package.wsgi
    master=on


You can also provided a set of eggs explicitly using the ``eggs``
option, i.e.::

    [buildout]
    parts=uwsgi

    [uwsgi]
    recipe=infrae.uwsgi
    download-url=http://projects.unbit.it/downloads/uwsgi-1.4.9.tar.gz
    eggs=my_uwsgi_package

.. _uWSGI: http://uwsgi-docs.readthedocs.org/
