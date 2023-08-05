TWLogger
========

TWLogger is a Python client for `TaskWorkshop <https://taskworkshop.com>`_
exceptions tracking system.

Installation
------------

Install with pip::

	$ pip install twlogger

Or add ``twlogger`` to the list of required packages in the ``setup.py`` file.


Configuration
-------------

You can use TWLogger as a WSGI middleware, as a logging handler or directly
via Client object.  For each configuration type you need to pass API URL or you
can set it as ``TWLOGGER_URL`` environment variable.  The URL should look like
this::

    https://taskworkshop.com/exceptions/log/API_KEY

As a WSGI Middleware
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    >>> from twlogger.middleware import TaskWorkshopMiddleware
    >>> error_catching_wsgi_app = TaskWorkshopMiddleware(wsgi_app)

In a PasteDeploy pipeline
~~~~~~~~~~~~~~~~~~~~~~~~~

::

    [filter:twlogger]
    use = egg:TWLogger#twlogger
    url = https://taskworkshop.com/exceptions/log/YOUR_TOKEN

    [pipeline:main]
    pipeline =
        twlogger
        your-app

    [app:your-app]
    ...

As a logging handler
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    >>> import logging
    >>> from twlogger.handler import TWLoggerHandler
    >>> handler = TWLoggerHandler()
    >>> logger = logging.getLogger(__name__)
    >>> logger.addHandler(handler)

Using **logging.config.dictConfig**:

.. code-block:: python

    LOGGING = {
        'version': 1,
        'disable_existing_loggers': True,

        'formatters': {
            'console': {
                'format': ('%(asctime)s %(levelname)s '
                           '[%(name)s][%(threadName)s] %(message)s'),
            },
        },

        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'DEBUG',
                'formatter': 'console'
            },
            'twlogger': {
                'class': 'twlogger.handler.TWLoggerHandler',
                'url': 'https://taskworkshop.com/exceptions/log/YOUR_TOKEN',
                'level': 'ERROR',
            },
        },

        'loggers': {
            'root': {
                'handlers': ['console', 'twlogger'],
                'level': 'DEBUG',
                'propagate': True,
            },
            'twlogger': {
                'handlers': ['console'],
                'level': 'DEBUG',
                'propagate': False,
            },
            'twlogger.error': {
                'handlers': ['console'],
                'level': 'DEBUG',
                'propagate': False,
            },
        },
    }

Using **logging.config.fileConfig**::

    [loggers]
    keys = root, twlogger, twlogger_error

    [handlers]
    keys = console, twlogger

    [formatters]
    keys = console

    [formatter_console]
    format = %(asctime)s %(levelname)s [%(name)s][%(threadName)s] %(message)s

    [handler_console]
    class = StreamHandler
    args = (sys.stderr,)
    level = DEBUG
    formatter = console

    [handler_twlogger]
    class = twlogger.handler.TWLoggerHandler
    args = ('https://taskworkshop.com/exceptions/log/YOUR_TOKEN', )
    level = ERROR
    formatter = console

    [logger_root]
    handlers = console, twlogger
    level = DEBUG

    [logger_twlogger]
    level = DEBUG
    handlers = console
    qualname = twlogger
    propagate = 0

    [logger_twlogger_error]
    level = DEBUG
    handlers = console
    qualname = twlogger.error
    propagate = 0


Manual usage
------------

Logger: handling exceptions
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Exception info and extra data will be submitted with the event.

.. code-block:: python
    
    >>> import logging
    >>> logger = logging.getLogger(__name__)
    >>> try:
    ...     x / y
    ... except ZeroDivisionError:
    ...     logger.exception('Division by zero!', extra={'x': x, 'y': y})

Logger: sending events
~~~~~~~~~~~~~~~~~~~~~~

You can submit events of any level:

.. code-block:: python

    >>> import logging
    >>> logger = logging.getLogger(__name__)
    >>> logger.error('Some error')
    >>> logger.warn('Some warning.')
    >>> logger.info('Some info.', extra={'foo': 'bar'})

Client: handling exceptions
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    >>> from twlogger.client import Client
    >>> client = Client()
    >>> try:
    ...     1 / 0
    ... except ZeroDivisionError:
    ...     client.capture_exception()
    >>> try:
    ...     x / y
    ... except ZeroDivisionError:
    ...     client.capture_exception(x=x, y=y)

Client: sending events
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    >>> from twlogger.client import Client
    >>> client = Client()
    >>> client.log_event('info', 'Some info log',
    ...                  place='File: "/foo/bar.py", line: 71, in foo_bar')


Issues and questions
--------------------

Have a bug? Please create an issue on GitHub!

https://github.com/TaskWorkshop/taskworkshop-logger-python/issues

Contributing
------------

TWLogger is an open source software and your contribution is very much
appreciated.

1. Check for
   `open issues <https://github.com/TaskWorkshop/taskworkshop-logger-python/issues>`_ or
   `open a fresh issue <https://github.com/TaskWorkshop/taskworkshop-logger-python/issues/new>`_
   to start a discussion around a feature idea or a bug.
2. Fork the
   `repository on Github <https://github.com/TaskWorkshop/taskworkshop-logger-python>`_
   and make your changes.
3. Write tests for your changes and follow these rules: PEP8, PEP257 and The
   Zen of Python.
4. Make sure to add yourself to AUTHORS and send a pull request.

Use ``pytest-cov``, ``pytest-pep8`` and ``pytest-flakes`` PyTest extensions
when running your tests:

.. code-block:: bash

    $ pip install pytest pytest-cov pytest-pep8 pytest-flakes
    $ py.test --cov twlogger --cov-report term-missing --pep8 --flakes


Licence
-------

TWLogger is available under the GPL version 2 license. See
`LICENSE <https://github.com/TaskWorkshop/taskworkshop-logger-python/blob/master/LICENSE>`_
file.
License is available at http://www.gnu.org/licenses/gpl-2.0.txt
