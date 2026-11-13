"""Tests for webinput, run both standalone and embedded.

This ``tests`` directory is a package (has this ``__init__.py``) so that pytest
imports the test modules under a fully-qualified name (``webinput.tests.*`` when
webinput is checked out on its own, or ``<parent>.lib.webinput.tests.*`` when it
is embedded as a submodule).  The test modules therefore use relative imports
(``from ..src.helper_webserve_logging import ...``) and always reach webinput's
own ``src`` package, never a same-named ``src`` package that a parent project may
also define on ``sys.path``.
"""
