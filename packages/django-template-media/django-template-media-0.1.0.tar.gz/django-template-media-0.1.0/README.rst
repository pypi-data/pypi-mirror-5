django-template-media
=======================

This module allows template writers to manipulate form media in templates.
This allows multiple forms on a page to share scripts with out including them twice.

All of the media included in the page using these tools
are collected into a single 'global'[1]_ ``Media`` instance for that page.
All operations are performed on this 'global'[1]_ ``Media`` instance.

Installing
==========

Install this package, using pip::

    $ pip install django-template-media

Add it to your ``INSTALLED_APPS``::

    INSTALLED_APPS += (
        'django_template_media',
    )

Load the template tags in your templates by loading the ``media_tags`` library::

    {% load media_tags %}

Using
=====

The tools are designed to work with the template heirarchy in a sane manner.
The examples will assume a ``site.html`` base template that defines a block named ``media``::

    <!doctype html>
    <html>
        {% load media_tags %}
        <head>
            <title>Example site</title>
            {% block media %}
                {% print_media %}
            {% endblock %}
        </head>
        <body>
            {% block body %}
        </body>
    </html>


Printing the media
------------------

As shown in the above example,
the ``{% print_media %}`` tag prints all of the media accumulated on the page so far.
It should only be called once per page.
A sensible place to put this is in your base template.

Building media in the template
------------------------------

If you want to construct an ad-hoc media instance,
for site-wide media or such things,
you can use the ``{% media %}`` block.
The ``Media()`` instance generated will be added to the current page media::

    {% extends "site.html" %}

    {% load media_tags %}

    {% block media %}
        {% media %}
            {% add_js "jquery.js" %}
            {% add_js "jquery.lib.js" %}

            {% add_js "bootstrap.js" %}
            {% add_js "bootstrap.lib.js" %}

            {% add_css "screen" "bootstrap.css" %}
            {% add_css "screen" "site.css" %}
            {% add_css "print" "print.css" %}

            {% if user.is_anonymous %}
                {% add_media login_form.media %}
            {% endif %}
        {% endmedia %}

        {# This is called **after** adding all the media #}
        {{ block.super }}
    {% endblock %}

The three possible tags in the ``{% media %}`` block are as follows:

``{% add_js path %}``
    Add the JavaScript file ``path`` to the media.
    Multiple files can be specified in the one tag,
    or just place them one after another as a series of tags.

``{% add_css media_type path %}``
    Add the CSS file ``path`` to the media, with ``media_type``.
    Multiple files can be specified in the one tag,
    or just place them one after another as a series of tags.

``{% add_media media %}``
    Adds the named form media to the current media.
    Multiple media instances can be added at once by naming them all.
    or just place them one after another as a series of tags.

Adding media from forms
-----------------------

If you just want to add a single JavaScript file or CSS file,
or a single form media instance,
you do not need to wrap everything in a ``{% media %}`` block::

    {% extends 'site.html' %}

    {% load media_tags %}

    {% block body %}
        <form action='.' method='post'>
            {% csrf_token %}
            {{ form }}
            <input type="submit">
        </form>
    {% endblock %}

    {% block media %}
        {% add_media form.media %}
        {{ block.super }}
    {% endblock %}

The ``{% add_media %}`` tag accepts multiple media instances,
so if you have multiple forms, you can add the media for all of them at once::

    {% add_media form_1.media form_2.media %}

Working with template hierarchies
---------------------------------

In sub-templates, the call to ``{{ block.super }}``
*must* be placed *after* all calls that modify the media.
As the media is printed out in an ancestor's ``{% block media %}``,
the sub-template must add all of the media it needs
before calling ``{{ block.super }}``.

``{% add_js %}``, ``{% add_css %}`` and ``{% add_media %}`` tags outside of
``{% media %}`` blocks always *prepend* new media to the current page media.
This is because templates are rendered from the child to the parent,
and parent media should precede child media.
Thus, if you have multiple ``{% add_media %}`` or ``{% media %}`` tags in once page,
the media will be printed out in reverse order to its appearance on the page.
As such, you are encouraged to have only one
``{% add_media %}`` or ``{% media %}`` block per template,
to prevent confusion.

In a ``{% media %}`` block, calls to ``{% add_media %}``, ``{% add_js %}`` and
``{% add_css %}`` append media to the current ad-hoc media instance.

------------------------

.. [1]
   The 'global' ``Media`` instance is stored in the currently rendering template context.
   It is only global to the whole page that is currently being constructed,
   not across all templates.
