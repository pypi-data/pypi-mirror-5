django-caddstat
===============

.. image:: https://travis-ci.org/oess/django-caddstat.png?branch=master
     :target: https://travis-ci.org/oess/django-caddstat
.. image:: https://coveralls.io/repos/oess/django-caddstat/badge.png?branch=master
    :target: https://coveralls.io/r/oess/django-caddstat

Statistics for your Computer Aided Drug Design projects as a django specific package. View CADD Stat
now: http://caddstat.eyesopen.com

Roadmap
-------

The aim of CADD Stat is to cover all the statistics covered in the
`placemat <https://openeye.app.box.com/s/wjkd01azigh4ie6q7f64>`_ that was present at the conference.

Bugs
----

If you find a bug please send feedback via the app `itself <http://caddstat.eyesopen.com/feedback/>`_, or log an
`issue <https://github.com/oess/django-caddstat/issues>`_. If you know how to fix the bug feel free to make to fork
the repo and submit a pull request, see below.

Contributing
------------

Contributions are welcome as a pull request. Do not forget to add yourself to the AUTHORS file. Learn more
about GitHub `pull requests <https://help.github.com/articles/using-pull-requests>`_. All contributions are subject
the same license as CADD Stat. To create suitable development environment in a virtualenv run
``pip install -r requirements.txt``. Please run the test suite before submitting a pull request::

  python runtests.py
  # or
  python setup.py test

You can test against multiple Django versions by running ``tox`` or run in parallel with ``detox``. Check our test
coverage by running::

  coverage run runtests.py

Licensing
---------

CADD Stat is provided with a BSD 3-clause license, see
the `LICENSE <https://github.com/oess/django-caddstat/blob/master/LICENSE>`_ file for full details. In addition it
utilizes numerous other python open source libraries all of which are listed in
`requirements.txt <https://github.com/oess/django-caddstat/blob/master/requirements.txt>`_.

Acknowledgements
----------------

* `Bootstrap <http://getbootstrap.com/>`_ for the look and feel using the `Apache license <https://github.com/twbs/bootstrap/blob/master/LICENSE>`_.
* Inspiration for the django app layout taken from `django-app-template <https://github.com/mlavin/django-app-template>`_ and `cookiecutter-djangopackage <https://github.com/pydanny/cookiecutter-djangopackage>`_.
* `HTML5 Boilerplate <http://html5boilerplate.com/>`_ for HTML5 layout.
* `GitHub Buttons <http://ghbtns.com>`_ for the watch and fork buttons.

Change Log
----------

* 0.1 (09/16/13)

  * Initial release with feedback from the GRC conference.
  * Added Pearson and Cohen's size effect tests.

Installation
------------

Grab the latest released version from PyPi and install into a `virtualenv <http://www.virtualenv.org>`_::

  pip install django-caddstat
  pip install django-caddstat[numpy]
  pip install django-caddstat[statslibs]
  pip install django-caddstat[statsmodels]

Multiple installation steps are required because of the way the scientific python ecosystem handles packaging. Note that
Numpy and SciPy have multiple system dependencies (e.g. Fortran) which must be met before using pip. Read more on the
`SciPy <http://www.scipy.org/install.html>`_ website.

To install the development version of CADD Stat you must install like this::

  pip install -e git+https://github.com/oess/django-caddstat.git#egg=django-caddstat
  pip install -e git+https://github.com/oess/django-caddstat.git#egg=django-caddstat[numpy]
  pip install -e git+https://github.com/oess/django-caddstat.git#egg=django-caddstat[statslibs]
  pip install -e git+https://github.com/oess/django-caddstat.git#egg=django-caddstat[statsmodels]

Create or use an existing Django project::

  pip install django
  django-admin.py startproject mysite
  cd mysite/mysite

Add ``caddstat`` and ``analytical`` to your ``INSTALLED_APPS`` in ``settings.py``::

    INSTALLED_APPS = (
      ...
      'analytical',
      'caddstat',
    )

Add an entry to your project ``urls.py``::

    urlpatterns = patterns(
        '',
        url(r'^', include('caddstat.urls')),
        ...
    )


In this example CADD Stat will now be available on the root of your web site, e.g. http://127.0.0.1:8000. You can start
a local webserver with::

 python manage.py runserver 8000

Note CADD Stat uses `Celery <http://www.celeryproject.org/>`_ to place all statistical tests in a queue. The above example
does *not* use celery.

The feedback form (http://127.0.0.1:8000/feedback/) will send an email to the address specified in the setting
``CADDSTAT_FEEDBACK_EMAIL``, the default is test@example.com. Set a new value in your ``settings.py``. Ensure you have
configured a email backend within your project first, see https://docs.djangoproject.com/en/dev/topics/email/ for more
information.