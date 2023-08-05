TheHerk Article
===============

TheHerk Article is a very simple django CMS plugin for posting an article that consists of:

- Title
- Slugged Title
- Description
- Body (html)

By default the title field and description will populate an hgroup, but this can be overwritten in your template. The slug is to link the title to an ID on the page.

The slug is set to only save on create so that the link won't change over time and edits.

The body can use html, but this, too, can be changed in your template.

Usage
-----

1. Add "article" to your INSTALLED_APPS

        INSTALLED_APPS = (
            ...
            'article',
        )

2. Run `python manage.py migrate article`.

   Alternately, you could `syncdb` and `migrate --fake`
