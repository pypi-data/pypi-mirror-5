Contributing
============

Please file bugs to the `Github issue tracker`_.  Pull requests are welcome.

.. _Github issue tracker: https://github.com/treyhunner/pep438/issues


Hacking and Pull Requests
-------------------------

Please try to conform to `PEP8`_ for code contributions and ensure that the
tests continue to function.

Please include new tests with your pull requests when appropriate.

Feel free to open pull requests before you've finished your code or tests.
Opening your pull request sooner will allow others to comment on it sooner.

A checklist of things to remember when making a feature:

- Write tests if applicable
- Note important changes in the `CHANGES`_ file
- Update the `README`_ file if needed
- Update the documentation if needed
- Add yourself to the `AUTHORS`_ file

.. _AUTHORS: AUTHORS.rst
.. _CHANGES: CHANGES.rst
.. _README: README.rst

Running the tests
~~~~~~~~~~~~~~~~~

You will need `tox`_ and `coverage`_ installed to run the tests on your code:

.. code-block:: bash

    $ pip install tox coverage

To run the tests and generate a coverage report:

.. code-block:: bash

    $ make test

.. _pep8: http://www.python.org/dev/peps/pep-0008/
.. _tox: http://testrun.org/tox/latest/
.. _coverage: https://pypi.python.org/pypi/coverage/
