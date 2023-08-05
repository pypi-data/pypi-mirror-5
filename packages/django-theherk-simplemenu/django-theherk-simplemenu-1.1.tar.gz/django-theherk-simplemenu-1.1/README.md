TheHerk Simple Menu
===================

TheHerk Simple Menu is a very simple django CMS plugin for posting a quick and easy quick links menu. Nothing fancy; just a wherever you want menu with whatever links you want.

Usage
-----

1. Add "simplemenu" to your INSTALLED_APPS

        INSTALLED_APPS = (
            ...
            'simplemenu',
        )

2. Run `python manage.py migrate simplemenu`.

   Alternately, you could `syncdb` and `migrate --fake`
