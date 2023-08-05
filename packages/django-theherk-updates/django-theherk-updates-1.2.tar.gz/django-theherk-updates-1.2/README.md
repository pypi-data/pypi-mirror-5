TheHerk Updates
===============

TheHerk Updates is an application for tracking and displaying updates to anything; for instance, a website. You just add updates by date and description and then use the plugin to display them.

There is an apphook so you can attach the full update list to a menu URL.

Usage
-----

1. Add "updates" to your INSTALLED_APPS

        INSTALLED_APPS = (
            ...
            'updates',
        )

2. Run `python manage.py migrate updates`.

   Alternately, you could `syncdb` and `migrate --fake`
