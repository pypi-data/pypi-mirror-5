TheHerk Download
================

TheHerk Download is a very simple django CMS plugin for posting an a download link.

Usage
-----

1. Add "download" to your INSTALLED_APPS

        INSTALLED_APPS = (
            ...
            'download',
        )

2. Run `python manage.py migrate download`.

   Alternately, you could `syncdb` and `migrate --fake`
