.. _install:

Installation
============

Since ``CudaPyInt`` is a pure Python module, it should be pretty easy to install.
Make sure you have `numpy <http://numpy.scipy.org/>`_, `PyCUDA <http://wiki.tiker.net/PyCuda/Installation/Linux/>`_ and the `CUDA SDK <http://numpy.scipy.org/>`_ installed on your system before you start.


From source
-----------

Once you've downloaded and unpacked the source, you can navigate into the
root source directory and run:

::

    $ python setup.py build
    $ python setup.py install --user



You might need to run this using ``sudo`` depending on your Python
installation.
