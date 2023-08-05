Pretzel
-------

| |Build Status|
| |Coverage Status|

Is an asynchronous application framework for python

Features
--------

-  C# like async/await(async/yield) paradigm for asynchronous
   programming (monad base)
-  Cool asynchronous I/O loop implementation
-  Uniform asynchronous stream implementation for sockets and pipes
-  Interact with subprocesses asynchronously
-  Greenlet support (but not required)
-  Remote code executing over ssh or in child process (with only
   requirements python and ssh itself)
-  Python 2/3, PyPy compatible
-  Asynchronous python shell ``python -mpretzel.apps.shell`` (requires
   greenlet)

Installation
------------

| As git submodule:
| ``git submodule add git://github.com/aslpavel/pretzel.git <path_to_submodule>``
| Pip from git:
| ``pip install git+git://github.com/aslpavel/pretzel-pkg.git``
| Pip from PyPI
| ``pip install pretzel``

Examples
--------

-  `Simple echo server <https://gist.github.com/aslpavel/5635559>`__
-  `Cat remote file over
   ssh <https://gist.github.com/aslpavel/5635610>`__

.. |Build Status| image:: https://api.travis-ci.org/aslpavel/pretzel.png
   :target: https://travis-ci.org/aslpavel/pretzel
.. |Coverage Status| image:: https://coveralls.io/repos/aslpavel/pretzel/badge.png?branch=master
   :target: https://coveralls.io/r/aslpavel/pretzel?branch=master
