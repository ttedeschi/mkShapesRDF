
Join the development
====================



Linting and formatting
----------------------

We use ``black`` for formatting and ``flake8`` for linting.

You should run the formatting and the linting before committing your code, checking for errors/warnings and fixing them.

This is very important since the CI/CD pipeline will fail if the code is not formatted or if there are linting errors.


Running tests 
-------------

We use `pytest` for testing. The user should run the tests before committing the code.

You can run the tests with ``pytest`` or ``python -m pytest -n auto`` (parallel version).


pre-commit hooks
----------------

We use `pre-commit` to run the formatting and the linting before committing your code.

You might run ``pre-commit install`` to install the pre-commit hooks, 
this will run the formatting whenever a ``git commit`` is run.





The CI/CD pipeline
------------------

The CI/CD pipeline defined in ``.github/workflows/ci_lint_format_test.yml`` is run on every push to the repository.

It will run the tests, the linting and the formatting on github (with a private runner).


You might check the status of the pipeline on github (in the ``Actions`` tab) or with the badge 

|tests|

.. |tests| image:: https://github.com/giorgiopizz/mkShapesRDF/actions/workflows/ci_lint_format_test.yml/badge.svg
   :target: https://github.com/giorgiopizz/mkShapesRDF/actions/workflows/ci_lint_format_test.yml



Docs
----

In order to build the documentation you can run the command below in the root directory of mkShapesRDF:

.. code:: bash
  python -m sphinx -T -E -b html -d _build/doctrees -D language=en docs test_html
