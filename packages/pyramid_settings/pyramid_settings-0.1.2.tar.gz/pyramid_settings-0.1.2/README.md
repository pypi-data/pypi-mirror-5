pyramid_settings
================

`pyramid_settings` is simplest package (2 functions to be fair) that enables
you to load python modules as pyramid settings files.

TL;DR; You can ditch most of your .ini files and store your settings in
clean python.


Usage
-----

    from pyramid.config import Configurator

    from pyramid_settings import load_settings


    def main(global_config, **settings):
        """ This function returns a Pyramid WSGI application.

        """

        load_settings(__name__, settings, config=global_config)

        config = Configurator(settings=settings)
        config.scan()
        return config.make_wsgi_app()

and this is all you need (if you use paster ini files and pserv) to be able to use:

    $ pserv development.ini pysettings=settings.py,base.py,roman.py


Warning
-------

Everything you see here is work in progress and should not be ever used in
production (trust me - don't trust me). Contributions, critique, angry letters
and such are welcome.


Installation
------------

Install with pip::

    $ pip install pyramid_settings

Issues and questions
--------------------

Have a bug? Please create an issue on GitHub!

https://github.com/niktto/pyramid_settings/issues


Contributing
------------

EasyEmail is an open source software and your contribution is very much
appreciated.

1. Check for
   `open issues https://github.com/niktto/pyramid_settings/issues or
   `open a fresh issue https://github.com/niktto/pyramid_settings/issues/new
   to start a discussion around a feature idea or a bug.
2. Fork the
   `repository on Github https://github.com/niktto/pyramid_settings
   and make your changes.
3. Follow these rules: PEP8, PEP257 and The
   Zen of Python.
4. Make sure to add yourself to AUTHORS and send a pull request.


Licence
-------

EasyEmail is available under the New BSD License. See
LICENSE https://github.com/niktto/pyramid_settings/blob/master/LICENSE
file.