.. _api:

API
***

.. automodule:: cudapyint

This page details the methods and classes provided by the ``cudapyint`` module.



CudaPyInt Solver
-------------------------------------

.. autoclass:: cudapyint.Solver.Solver
   :members: _getOptimalGPUParam, solve

CudaPyInt ODE Solvers
-------------------------------------
Standard usage of ``CudaPyint`` involves instantiating an
:class:`ODESolver`.

.. autoclass:: cudapyint.ODESolver.ODESolver
   :members: __init__, _compile, _compileSourceModule, _solve_internal, _post_process_results, _copy_constants

To run ``CudaPyint`` with CUDA shared memory involves instantiating an
:class:`ODESolverSharedMemory`.

.. autoclass:: cudapyint.ODESolverSharedMemory.ODESolverSharedMemory
   :members:

CudaPyInt ODE Solvers for parallel integration
----------------------------------------------

To run ``CudaPyInt`` with parallel computation of equations within a system involves instantiating an
:class:`ParallelODESolver`.

.. autoclass:: cudapyint.ParallelODESolver.ParallelODESolver
   :members:

To run ``CudaPyInt`` with parallel computation of equations within a system with CUDA shared memory involves instantiating an
:class:`ParallelODESolver`.

.. autoclass:: cudapyint.ParallelODESolverSharedMemory.ParallelODESolverSharedMemory
   :members:


CudaPyInt Generator
-------------------------------------
Every CudaPyInt Solver uses an instance of the
:class:`CodeGenerator`.

.. autoclass:: cudapyint.CodeGenerator.CodeGenerator
   :members: __init__, _writeCode, _create_constants_fields

The CudaPyInt ODE Solver uses an Instance of the
:class:`CulsodaCodeGenerator`.

.. autoclass:: cudapyint.CulsodaCodeGenerator.CulsodaCodeGenerator
   :members: __init__, generate
   
CudaPyInt PyCudaUtils
-------------------------------------
Simple util class
:class:`Pycuda`.

.. autofunction:: cudapyint.PyCudaUtils.create_2D_array
.. autofunction:: cudapyint.PyCudaUtils.copy2D_host_to_array
.. autofunction:: cudapyint.PyCudaUtils.copy_host_to_device
 