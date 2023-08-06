FreePyBX is a web-configurator for FreeSWITCH. It comes with a complete
multi-tenant setup with individual PBX logins, CDR reporting and lots more. It
comes with example configurations that you can tweak. Check the website for
more information. Commercial support is also available.

Installation and Setup
======================

Install ``FreePyBX`` using easy_install::

    easy_install FreePyBX

Make a config file as follows::

    paster make-config FreePyBX config.ini

Tweak the config file as appropriate and then setup the application::

    paster setup-app config.ini

Then you are ready to go with::
    paster serve --reload ./config.ini


Access the app via your favorite web browser at http://127.0.0.1:8000




