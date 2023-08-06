PyFFT: FFT for PyCuda and PyOpenCL
==================================

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Introduction
============

This module contains implementation of batched FFT, ported from `Apple's OpenCL implementation
<https://developer.apple.com/mac/library/samplecode/OpenCL_FFT/index.html>`_.
OpenCL's ideology of constructing kernel code on the fly maps perfectly on
`PyCuda <http://mathema.tician.de/software/pycuda>`_/`PyOpenCL <http://mathema.tician.de/software/pyopencl>`_,
and variety of Python's templating engines makes code generation simpler. I used
`mako <http://pypi.python.org/pypi/Mako>`_ templating engine, simply because of
the personal preference. The code can be easily changed to use any other engine.

.. note:: "Cuda" part of ``pyfft`` requires ``PyCuda`` 0.94 or newer;
             "CL" part requires ``PyOpenCL`` 0.92 or newer.

Quick Start
===========

This overview contains basic usage examples for both backends, Cuda and OpenCL.
Cuda part goes first and contains a bit more detailed comments,
but they can be easily projected on OpenCL part, since the code is very similar.

... with PyCuda
~~~~~~~~~~~~~~~

First, import ``numpy`` and plan creation interface from ``pyfft``.

 >>> from pyfft.cuda import Plan
 >>> import numpy

Import Cuda driver API root and context creation function.
In addition, we will need ``gpuarray`` module to pass data to and from GPU.

 >>> import pycuda.driver as cuda
 >>> from pycuda.tools import make_default_context
 >>> import pycuda.gpuarray as gpuarray

Since we are using Cuda, it must be initialized before any Cuda functions are called
(by default, the plan will use existing context, but there are other possibilities;
see reference entry for :class:`~pyfft.cuda.Plan` for further information).
Stream creation is optional; if no stream is provided, :class:`~pyfft.cuda.Plan` will create its own one.

 >>> cuda.init()
 >>> context = make_default_context()
 >>> stream = cuda.Stream()

Then the plan must be created.
The creation is not very fast, mainly because of the compilation speed.
But, fortunately, ``PyCuda`` and ``PyOpenCL`` cache compiled sources,
so if you use the same plan for each run of your program, it will be compiled only the first time.

 >>> plan = Plan((16, 16), stream=stream)

Now, let's prepare simple test array:

 >>> data = numpy.ones((16, 16), dtype=numpy.complex64)
 >>> gpu_data = gpuarray.to_gpu(data)
 >>> print gpu_data # doctest: +ELLIPSIS
 [[ 1.+0.j  1.+0.j  1.+0.j  1.+0.j  1.+0.j  1.+0.j  1.+0.j  1.+0.j  1.+0.j
    1.+0.j  1.+0.j  1.+0.j  1.+0.j  1.+0.j  1.+0.j  1.+0.j]
 ...
  [ 1.+0.j  1.+0.j  1.+0.j  1.+0.j  1.+0.j  1.+0.j  1.+0.j  1.+0.j  1.+0.j
    1.+0.j  1.+0.j  1.+0.j  1.+0.j  1.+0.j  1.+0.j  1.+0.j]]

... and execute our plan:

 >>> plan.execute(gpu_data) # doctest: +ELLIPSIS
 <pycuda._driver.Stream object at ...>
 >>> result = gpu_data.get()
 >>> print result # doctest: +ELLIPSIS
 [[ 256.+0.j    0.+0.j    0.+0.j    0.+0.j    0.+0.j    0.+0.j    0.+0.j
      0.+0.j    0.+0.j    0.+0.j    0.+0.j    0.+0.j    0.+0.j    0.+0.j
      0.+0.j    0.+0.j]
 ...
  [   0.+0.j    0.+0.j    0.+0.j    0.+0.j    0.+0.j    0.+0.j    0.+0.j
      0.+0.j    0.+0.j    0.+0.j    0.+0.j    0.+0.j    0.+0.j    0.+0.j
      0.+0.j    0.+0.j]]

As expected, we got array with the first non-zero element, equal to array size.
Let's now perform the inverse transform:

 >>> plan.execute(gpu_data, inverse=True) # doctest: +ELLIPSIS
 <pycuda._driver.Stream object at ...>
 >>> result = gpu_data.get()

Since data is non-integer, we cannot simply compare it. We will just calculate error instead.

 >>> error = numpy.abs(numpy.sum(numpy.abs(data) - numpy.abs(result)) / data.size)
 >>> error < 1e-6
 True

That's good enough for single precision numbers.

Last step is releasing Cuda context:

 >>> context.pop()

... with PyOpenCL
~~~~~~~~~~~~~~~~~

OpenCL example consists of the same part as the Cuda one.

Import plan class:

 >>> from pyfft.cl import Plan
 >>> import numpy

Import OpenCL API root and array class:

 >>> import pyopencl as cl
 >>> import pyopencl.array as cl_array

Initialize context and queue (unlike Cuda one, OpenCL plan class requires either context
or queue to be specified; there is no "current context" in OpenCL):

 >>> ctx = cl.create_some_context(interactive=False)
 >>> queue = cl.CommandQueue(ctx)

Create plan (remark about caching in ``PyCuda`` applies here too):

 >>> plan = Plan((16, 16), queue=queue)

Prepare data:

 >>> data = numpy.ones((16, 16), dtype=numpy.complex64)
 >>> gpu_data = cl_array.to_device(ctx, queue, data)
 >>> print gpu_data # doctest: +ELLIPSIS
 [[ 1.+0.j  1.+0.j  1.+0.j  1.+0.j  1.+0.j  1.+0.j  1.+0.j  1.+0.j  1.+0.j
    1.+0.j  1.+0.j  1.+0.j  1.+0.j  1.+0.j  1.+0.j  1.+0.j]
 ...
  [ 1.+0.j  1.+0.j  1.+0.j  1.+0.j  1.+0.j  1.+0.j  1.+0.j  1.+0.j  1.+0.j
    1.+0.j  1.+0.j  1.+0.j  1.+0.j  1.+0.j  1.+0.j  1.+0.j]]

Forward transform:

 >>> plan.execute(gpu_data.data) # doctest: +ELLIPSIS
 <pyopencl._cl.CommandQueue object at ...>
 >>> result = gpu_data.get()
 >>> print result # doctest: +ELLIPSIS
 [[ 256.+0.j    0.+0.j    0.+0.j    0.+0.j    0.+0.j    0.+0.j    0.+0.j
      0.+0.j    0.+0.j    0.+0.j    0.+0.j    0.+0.j    0.+0.j    0.+0.j
      0.+0.j    0.+0.j]
 ...
  [   0.+0.j    0.+0.j    0.+0.j    0.+0.j    0.+0.j    0.+0.j    0.+0.j
      0.+0.j    0.+0.j    0.+0.j    0.+0.j    0.+0.j    0.+0.j    0.+0.j
      0.+0.j    0.+0.j]]

Inverse transform:

 >>> plan.execute(gpu_data.data, inverse=True) # doctest: +ELLIPSIS
 <pyopencl._cl.CommandQueue object at ...>
 >>> result = gpu_data.get()

Check that the result is equal to the initial data array:

 >>> error = numpy.abs(numpy.sum(numpy.abs(data) - numpy.abs(result)) / data.size)
 >>> print error < 1e-6
 True

``PyOpenCL`` does not require explicit context destruction, Python will do it for us.

Reference
=========

.. module:: pyfft

.. data:: VERSION

   Tuple with integers, containing the module version, for example ``(0, 3, 4)``.

.. module:: pyfft.cuda
.. class:: Plan(shape, dtype=numpy.complex64, mempool=None, context=None, \
		normalize=True, wait_for_finish=None, fast_math=True, stream=None)
.. module:: pyfft.cl
.. class:: Plan(shape, dtype=numpy.complex64, context=None, \
		normalize=True, scale=1.0, wait_for_finish=None, fast_math=True, queue=None)

   Creates class, containing precalculated FFT plan.

   :param shape: problem size. Can be integer or tuple with 1, 2 or 3 integer elements.
          Each dimension must be a power of two.

   :param dtype: numpy data type for input/output arrays. If complex data type is given,
          plan for interleaved arrays will be created. If scalar data type is given,
          plan will work for data arrays with separate real and imaginary parts.
          Depending on this parameter, :meth:`~pyfft.Plan.execute` will have different signatures;
          see its reference entry for details.

   :type dtype: numpy.complex64, numpy.float32, numpy.complex128, numpy.float64

   :param normalize: whether to normalize inverse FFT so that IFFT(FFT(signal)) == signal.
          If equals to ``False``, IFFT(FFT(signal)) == signal * x * y * z.

   :param scale: if set, the result of forward transform will be multiplied by ``scale``,
          and the result of backward transform will be divided by ``scale``.

   :param wait_for_finish: boolean variable, which tells whether it is necessary to wait
          on stream after scheduling all FFT kernels.
          Default value depends on ``context``, ``stream`` and ``queue``
          parameters --- see `Contexts and streams usage logic`_ for details.
          Can be overridden by ``wait_for_finish`` parameter to :meth:`~pyfft.Plan.execute`

   :param fast_math: if ``True``, additional compiler options will be used,
          which increase performance at the expense of accuracy.
          For Cuda it is ``-use_fast_math``, for OpenCL --- ``-cl-mad-enable``
          and ``-cl-fast-relaxed-math``. In addition, in case of OpenCL,
          ``native_cos`` and ``native_sin`` are used instead of ``cos`` and ``sin``
          (Cuda uses intrinsincs automatically when ``-use_fast_math`` is set).

   :param context: context, which will be used to compile kernels and execute plan.
          See `Contexts and streams usage logic`_ entry for details.

   :param mempool: *Cuda-specific*. If specified, method ``allocate`` of this object
          will be used to create temporary buffers.

   :param stream: *Cuda-specific*. An object of class ``pycuda.driver.Stream``,
          which will be used to schedule plan execution.

   :param queue: *OpenCL-specific*. An object of class ``pyopencl.CommandQueue``,
          which will be used to schedule plan execution.

   .. warning:: 2D and 3D plans with ``y`` == 1 or ``z`` == 1 are not supported at the moment.

.. currentmodule:: pyfft

.. method:: Plan.execute(data_in, data_out=None, inverse=False, batch=1, wait_for_finish=None)

.. method:: Plan.execute(data_in_re, data_in_im, data_out_re=None, data_out_im=None, \
		inverse=False, batch=1, wait_for_finish=None)

   Execute plan for given data. Function signature depends on the data type,
   chosen during plan creation.

   :param data_in, data_in_re, data_in_im: input array(s).
          For Cuda plan ``PyCuda``'s ``GPUArray`` or anything
          that can be cast to memory pointer is supported;
          for OpenCL ``Buffer`` objects are supported.

   :param data_out, data_out_re, data_out_im: output array(s).
          If not given, the execution will be performed in-place and the results
          will be stored in ``data_in`` or ``data_in_re``, ``data_in_im``.

   :param inverse: if ``True``, inverse transform will be performed.

   :param batch: number of data sets to process.
          They should be located successively in ``data_in``.

   :param wait_for_finish: whether to wait for scheduled FFT kernels to finish.
          Overrides setting, which was specified during plan creation.

   :returns: ``None`` if waiting for scheduled kernels;
             ``Stream`` or ``CommandQueue`` object otherwise.
             User is expected to handle this object with care,
             since it can be reused during the next call to :meth:`~pyfft.Plan.execute`.

Contexts and streams usage logic
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Plan behavior can differ depending on values of ``context``, ``stream``/``queue`` and
``wait_for_finish`` parameters. These differences should, in theory, make the module
more convenient to use.

``wait_for_finish`` parameter can be set on three levels. First, there is a default value
which depends on ``context`` and ``stream``/``queue`` parameters (see details below). It
can be overridden by explicitly passing it as an argument to constructor. This setting,
in turn, can be overridden by passing ``wait_for_finish`` keyword to :meth:`~pyfft.Plan.execute`.

----
Cuda
----

1. ``context`` and ``stream`` are ``None``:

  * Current (at the moment of plan creation) context and device will be used to create kernels.
  * ``Stream`` will be created internally and used for each :meth:`~pyfft.Plan.execute` call.
  * Default value of ``wait_for_finish`` is ``True``.

2. ``stream`` is not ``None``:

  * ``context`` is ignored.
  * ``stream`` is remembered and used.
  * :meth:`~pyfft.Plan.execute` will assume that context, corresponding to given stream is active at the time of the call.
  * Default value of ``wait_for_finish`` is ``False``.

3. ``context`` is not ``None``:

  * :meth:`~pyfft.Plan.execute` will assume that context, corresponding to given one is active at the time of the call.
  * New ``Stream`` is created each time :meth:`~pyfft.Plan.execute` is called and destroyed if ``wait_for_finish``
    finally evaluates to ``True``.
  * Default value of ``wait_for_finish`` is ``True``.

------
OpenCL
------

Either ``context`` or ``queue`` must be set.

1. ``queue`` is not ``None``:

  * ``queue`` is remembered and used.
  * Target context and device are obtained from ``queue``.
  * Default value of ``wait_for_finish`` is ``False``.

2. ``context`` is not ``None``:

  * ``context`` is remembered.
  * ``CommandQueue`` will be created internally and used for each :meth:`~pyfft.Plan.execute` call.
  * Default value of ``wait_for_finish`` is ``True``.

Performance
===========

Here is the comparison to pure Cuda program using CUFFT. For Cuda test program see
``cuda`` folder in the distribution. Pyfft tests were executed with ``fast_math=True``
(default option for performance test script).

In the following tables "sp" stands for "single precision", "dp" for "double precision".

Mac OS 10.6.6, Python 2.6, Cuda 3.2, PyCuda 2011.1, nVidia GeForce 9600M, 32 Mb buffer:

+---------------------------+------------+------------+
| Problem size / GFLOPS     | CUFFT, sp  | pyfft, sp  |
+===========================+============+============+
| [16, 1, 1], batch 131072  | 12.3       | 7.7        |
+---------------------------+------------+------------+
| [1024, 1, 1], batch 2048  | 19.9       | 15.7       |
+---------------------------+------------+------------+
| [8192, 1, 1], batch 256   | 13.0       | 12.3       |
+---------------------------+------------+------------+
| [16, 16, 1], batch 8192   | 10.6       | 10.0       |
+---------------------------+------------+------------+
| [128, 128, 1], batch 128  | 14.4       | 15.1       |
+---------------------------+------------+------------+
| [1024, 1024, 1], batch 2  | 15.6       | 13.4       |
+---------------------------+------------+------------+
| [16, 16, 16], batch 512   | 10.2       | 11.4       |
+---------------------------+------------+------------+
| [32, 32, 128], batch 16   | 15.2       | 15.7       |
+---------------------------+------------+------------+
| [128, 128, 128], batch 1  | 12.7       | 14.5       |
+---------------------------+------------+------------+

Ubuntu 10.04.2, Python 2.6.5, Cuda 3.2, PyCuda 2011.1, nVidia Tesla C2050, 32 Mb buffer:

+---------------------------+------------+------------+------------+------------+
| Problem size / GFLOPS     | CUFFT, sp  | pyfft, sp  | CUFFT, dp  | pyfft, dp  |
+===========================+============+============+============+============+
| [16, 1, 1], batch 131072  | 127.1      | 91.4       | 28.3       | 37.8       |
+---------------------------+------------+------------+------------+------------+
| [1024, 1, 1], batch 2048  | 316.2      | 254.0      | 75.9       | 28.4       |
+---------------------------+------------+------------+------------+------------+
| [8192, 1, 1], batch 256   | 250.6      | 117.3      | 94.7       | 29.3       |
+---------------------------+------------+------------+------------+------------+
| [16, 16, 1], batch 8192   | 119.7      | 106.7      | 39.4       | 43.4       |
+---------------------------+------------+------------+------------+------------+
| [128, 128, 1], batch 128  | 198.7      | 187.2      | 53.4       | 47.4       |
+---------------------------+------------+------------+------------+------------+
| [1024, 1024, 1], batch 2  | 184.4      | 168.5      | 73.7       | 27.7       |
+---------------------------+------------+------------+------------+------------+
| [16, 16, 16], batch 512   | 117.6      | 117.6      | 45.0       | 47.0       |
+---------------------------+------------+------------+------------+------------+
| [32, 32, 128], batch 16   | 161.6      | 163.9      | 63.2       | 58.8       |
+---------------------------+------------+------------+------------+------------+
| [128, 128, 128], batch 1  | 191.2      | 184.7      | 52.2       | 44.6       |
+---------------------------+------------+------------+------------+------------+
