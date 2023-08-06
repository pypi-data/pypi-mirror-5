.. CudaPyInt documentation master file

CudaPyInt
=========

Cuda-based Python integrater
----------------------------

CudaPyInt is a library based on PyCUDA and CULSODA which gives you the possibility to integrate ODE's in parallel on GPGPUs

Basic Usage
-----------

If you wanted to integrate a system, you would do something like:

::

    import numpy
    import cudapyint
    constants = {"a": 1.7,
                "b": 2.4,}
    timepoints = numpy.array(numpy.logspace(-4,0,10),dtype=numpy.float64)
    args=numpy.array(numpy.logspace(-1,0,10),dtype=numpy.float32).reshape(10,1)
    y0s = numpy.ones([10,2], numpy.float32)
    solver = cudapyint.ODESolver(cudaCodePath, constants)
    result, info = solver.solve(y0s, timepoints, args, mxstep=1000000,  
            use_jacobian=False, timing=True, info=True,  
            full_output=True, write_code=True)

User Guide
----------

.. toctree::
   :maxdepth: 2

   user/install

API Documentation
-----------------

.. toctree::
   :maxdepth: 2

   api
   
Contributors
------------

.. include:: ../../AUTHORS.rst


Changelog
---------

.. include:: ../../HISTORY.rst

License
-------
CudaPyInt is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

CudaPyInt is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with CudaPyInt.  If not, see <http://www.gnu.org/licenses/>.
