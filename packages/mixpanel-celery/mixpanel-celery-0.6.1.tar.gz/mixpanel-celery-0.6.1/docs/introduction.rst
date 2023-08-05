===========================================================
 mixpanel-celery - Asynchronous event tracking for Mixpanel
===========================================================

:Version: |release|

Introduction
============

mixpanel-celery helps you use `Celery`_ to asynchronously track your `Mixpanel`_
events. You want to perform your tracking asynchronously, because waiting for HTTP
requests to Mixpanel to complete every time you want to record something important
isn't ideal when you've already worked so hard to tune your performance.

mixpanel-celery works great with Django, but because Celery works with just
python, so does mixpanel-celery.

Installation
============

The easiest way to install the current development version of mixpanel-celery is
via `pip`_

Installing The Stable Version
-----------------------------

.. code-block:: bash

    $ pip install mixpanel-celery


Running The Test Suite
======================

We use Tox to test across all of our supported environments.

.. code-block:: bash

    $ pip install tox
    $ tox

If you'd just like to test for the version of python and Celery that you use,
install the appropriate requirements listed in the ``requirements`` folder, and
then run your tests. eg.

.. code-block:: bash

    $ pip install -r requirements/test_celery_default.txt
    $ pip install -r requirements/test_django_default.txt
    $ python setup.py test

Right now, the test suite requires Django, but we'd love a pull request to
remove that requirement.

It is also possible to run specific tests using ``nosetests`` directly.

Configuration
=============

For easy test usage with Django, set your Mixpanel api token in your project's
``settings.py`` file with the ``MIXPANEL_API_TOKEN`` variable. Then set::

    CELERY_ALWAYS_EAGER = True

So that all of your `Celery`_ tasks will run in-line for now.

Then add ``mixpanel`` to your list of ``INSTALLED_APPS``.

Note: Obviously you'll want to actually configure `Celery`_ using one of the
many available backends for actual production use and `Celery`_ has great
documentation on that.

Usage
=====

Basic python example tracking an event called ``my_event``

.. code-block:: python

    from mixpanel.tasks import EventTracker

    result = EventTracker.delay(
        'my_event',
        {'distinct_id': 1},
        token='YOUR_API_TOKEN',
    )
    result.wait()


Example usage in a Django view

.. code-block:: python

    from mixpanel.tasks import EventTracker
    from django.shortcuts import render

    def test_view(request, template='test/test_view.html'):
        """
        Show user a test page.
        """
        # We should record that the user hit this page
        EventTracker.delay('hit_test_view', {'distinct_id': request.user.pk})

        return render(template)


To pass the API key to your templates where you probably use the Mixpanel
Javascript API, add the context_processor to your settings file

.. code-block:: python

    TEMPLATE_CONTEXT_PROCESSORS = (
        # ...
        'mixpanel.context_processors.api_key',
        # ...
    )


Now in your templates you can access the API key like this

.. code-block:: javascript

    mixpanel.init("{{ MIXPANEL_API_TOKEN }}");


Building the Documentation
==========================

mixpanel-celery uses `sphinx`_ for documentation. To build the HTML docs

.. code-block:: bash

    $ pip install sphinx
    $ pip install sphinxtogithub
    $ cd /path/to/mixpanel-celery/docs
    $ make html

Bug Tracker
===========

If you have feedback about bugs, features or anything else, the github issue
tracking is a great place to report them:
http://github.com/winhamwr/mixpanel-celery/issues

License
=======

This software is licensed under the ``New BSD License``. See the ``LICENSE``
file in the top distribution directory for the full license text.

Versioning
==========

This project uses `Semantic Versioning`_.

.. _`Celery`: http://ask.github.com/celery/
.. _`Mixpanel`: http://mixpanel.com/
.. _`sphinx`: http://sphinx.pocoo.org/
.. _`online mixpanel-celery documentation`: http://winhamwr.github.com/mixpanel-celery/
.. _`Semantic Versioning`: http://semver.org/
.. _`pip`: http://pypi.python.org/pypi/pip
.. _`RabbitMQ`: http://www.rabbitmq.com/
