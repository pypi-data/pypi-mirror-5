Cask
====

.. image:: https://travis-ci.org/jstasiak/cask.png?branch=master
   :alt: Build status
   :target: https://travis-ci.org/jstasiak/cask

*Cask* is Injector-enabled, Python application microframework modelled after Flask.

It's purpose is to make the amount of boilerplate you need to write when developing your application smaller. Here's a simple example:

.. code-block:: python

    >>> from cask import Cask
    >>> from injector import inject
    >>>
    >>> def configure(binder):
    ...     binder.bind(str, to='ABC')
    ...
    >>> @Cask.run_main(modules=[configure])
    ... @inject(s=str)
    ... def main(s):
    ...     print(s)
    ...
    ABC


``Cask.run_main`` (it works both as class and instance method, see below) does the ``if __name__ == '__main__'`` check for you. So this

.. code-block:: python

    >>> app = Cask()
    >>> @app.run_main
    ... def main():
    ...     print(111)
    ...
    111

is shorter version of

.. code-block:: python

    >>> app = Cask()
    >>> @app.main
    ... def main():
    ...     print(222)
    ...
    >>> if __name__ == '__main__':
    ...     app.run()
    ...
    222


Construction
------------

``Cask`` constructor and ``Cask.run_main`` class method accept the following optional keyword arguments:

* ``modules`` - iterable of Injector modules, defaults to empty sequence
* ``injector``- instance of Injector to configure and use, by default new instance will be created for you

Hooks
-----

``Cask`` instance provides the following decorators allowing you to register hooks (note that you can inject into registered functions):

* ``Cask.before_main`` - should expect no parameters, if non-None value is returned application execution main function won't be executed
* ``Cask.after_main`` - should expect single ``result`` parameter and return processed result (modified or not)
* ``Cask.exception_handler(ExceptionCLass)`` - will handle exception raised during the application execution, should expect single argument called ``e`` and containing exception value:

  .. code-block:: python

      >>> app = Cask()
      >>> @app.exception_handler(Exception)
      ... def handle(e):
      ...     print('got exception %s' % (e,))
      ...
      >>> @app.run_main
      ... def main():
      ...     raise Exception(123)
      ...
      got exception 123

* ``Cask.main`` - main function should expect no arguments and may return something


You can, of course, register more than one callable for hooks other than ``main``.

.. note:: Only first matching ``exception_handler`` hook will be called, if any.

Execution
---------

This is what happens when you run Cask-based application:

#. Injector is configured using provided ``modules``
#. ``before_main`` hooks are called
#. If ``before_main`` hooks didn't return value different than None, ``main`` hook is executed
#. ``after_main`` hooks are called


Copyright
---------

Copyright (C) 2013 Jakub Stasiak

This source code is licensed under MIT license, see LICENSE file for details.
