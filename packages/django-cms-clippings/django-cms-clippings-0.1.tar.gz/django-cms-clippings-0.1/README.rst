=========
Clippings
=========
Clippings is a lightweight version of a Django-CMS Placeholder container (in 
other words a minimalist Page). It contains a single Placeholder named "content" 
and is designed to be used in external applications where you want display 
snippets of content that are also editable from the Django admin.

Features
--------

* Clippings are displayed using the show_clipping template tag. The name of
  the clipping is passed as an argument.

* Clippings display content from one or more plugins. Any plugin supported
  by Django-CMS can be used in a Clipping.

* If a Clipping cannot be found for a given name then an empty string is
  returned. This makes it easy to deal with optional content.

* Clippings are editable in the Django admin in the same way as Placeholders.
  Content can be created for any language supported in the project.

* Clippings are ideal for small sections of content. That keeps the number
  of Pages in a Django-CMS site as small as possible, avoiding any scalability
  issues.

* Settings such as REPORT_MISSING_CLIPPING can be used to catch cases where
  the content was set for one language but left empty for the others supported
  by a site.

The advantage compared to using `external placeholders <http://docs.django-cms.org/en/2.4.2/extending_cms/placeholders.html>`_,
is that there are no intermediate models mapping the slot in the template to
Placeholder objects. That means that the clippings can be used anywhere and
everywhere outside the CMS with no management overhead. However there is a
downside to this flexibility - Clippings are only editable from the admin. You
cannot edit them in-place on the page.

Example
-------

Clippings are displayed in Django templates using the show_clipping template
tag and take a single argument - the identifier (unique for a given site)
assigned to the Clipping when it was created::

    {% show_clipping "clipping" %}

Using the 'with' tag makes it easy to display clippings using variables passed
in the template context::

    {% with date|date:"Y-m" as datestr %}
        {% with "news-"|add:datestr|add:"-review" as identifier %}
            {% show_clipping identifier %}
        {% endwith %}
    {% endwith %}

Here we generate the reverse_id string from a date e.g. "news-2013-09-review".

Internationalization
--------------------
Clippings uses a Django-CMS placeholder so content can be fully
internationalized in all the languages supported by the project site.

Requirements
------------
Clippings source is based on the show_placeholder template tag from Django-CMS 
Version 2.4.2 and currently has only been tested with that version.

Installation
------------
Clippings is available on Pypy so installation is as easy as::

    pip install django-cms-clippings

You can also get the latest source from Github::

    git@github.com:StuartMacKay/django-cms-clippings.git

The add the app to INSTALLED_APPS in your settings file::

    INSTALLED_APPS = (
        ...
        'clippings',
        ...
    )

Settings
--------
Clippings uses the following settings::

    REPORT_MISSING_CLIPPING = True | False

If True and a clipping with the identifier cannot be found then an error is 
reported.

Error reporting varies depending on the value of settings.DEBUG. If it is True
then an exception is raised. If it is False an email is sent to the admins if
the SEND_BROKEN_LINK_EMAILS setting is also True.

