***************
Release history
***************


0.3.6 (9 Aug 2013)
==================

* ADDED: the first argument to the ``Transformation`` or ``PureParallel`` snippet is now a ``reikna.core.Indices`` object instead of a list.

* ADDED: classmethod ``PureParallel.from_trf()``, which allows one to create a pure parallel computation out of a transformation.

* FIXED: improved ``Computation.compile()`` performance for complicated computations by precreating transformation templates.


0.3.5 (6 Aug 2013)
==================

* FIXED: bug with virtual size algorithms returning floating point global and local sizes in Py2.


0.3.4 (3 Aug 2013)
==================

* CHANGED: virtual sizes algorithms were rewritten and are now more maintainable.
  In addition, virtual sizes can now handle any number of dimensions of local and global size,
  providing the device can support the corresponding total number of work items and groups.

* CHANGED: id- and size- getting kernel functions now have return types corresponding to their equivalents.
  Virtual size functions have their own independent return type.

* CHANGED: ``Thread.compile_static()`` and ``ComputationPlan.kernel_call()`` take global and local sizes in the row-major order, to correspond to the matrix indexing in load/store macros.

* FIXED: requirements for PyCUDA extras (a currently non-existent version was specified).

* FIXED: an error in gamma distribution sampler, which lead to slightly wrong shape of the resulting distribution.


0.3.3 (29 Jul 2013)
===================

* FIXED: package metadata.


0.3.2 (29 Jul 2013)
===================

* ADDED: same module object, when being called without arguments from other modules/snippets, is rendered only once and returns the same prefix each time.
  This allows one to create structure declarations that can be used by functions in several modules.

* ADDED: reworked :py:mod:`~reikna.cbrng` module and exposed kernel interface of bijections and samplers.

* CHANGED: slightly changed the algorithm that determines the order of computation parameters after a transformation is connected to it.
  Now the ordering inside a list of initial computation parameters or a list of a single transformation parameters is preserved.

* CHANGED: kernel declaration string is now passed explicitly to a kernel template as the first parameter.

* FIXED: typo in FFT performance test.

* FIXED: bug in FFT that could result in changing the contents of the input array to one of the intermediate results.

* FIXED: missing data type normalization in :py:func:`~reikna.cluda.dtypes.c_constant`.

* FIXED: Py3 incompatibility in ``cluda.cuda``.

* FIXED: updated some obsolete computation docstrings.


0.3.1 (25 Jul 2013)
===================

* FIXED: too strict array type check for nested computations that caused some tests to fail.

* FIXED: default values of scalar parameters are now processed correctly.

* FIXED: Mako threw name-not-found exceptions on some list comprehensions in FFT template.

* FIXED: some earlier-introduced errors in tests.

* INTERNAL: ``pylint`` was ran and many stylistic errors fixed.


0.3.0 (23 Jul 2013)
===================

Major core API change:

* Computations have function-like signatures with the standard ``Signature`` interface; no more separation of inputs/outputs/scalars.

* Generic transformations were ditched; all the transformations have static types now.

* Transformations can now change array shapes, and load/store from/to external arrays in output/input transformations.

* No flat array access in kernels; all access goes through indices.
  This opens the road for correct and automatic stride support (not fully implemented yet).

* Computations and accompanying classes are stateless, and their creation is more straightforward.

Other stuff:

* Bumped Python requirements to >=2.6 or >=3.2, and added a dependency on ``funcsig``.

* ADDED: more tests for cluda.functions.

* ADDED: module/snippet attributes discovery protocol for custom objects.

* ADDED: strides support to array allocation functions in CLUDA.

* ADDED: modules can now take positional arguments on instantiation, same as snippets.

* CHANGED: ``Elementwise`` becomes :py:class:`~reikna.pureparallel.PureParallel` (as it is not always elementwise).

* FIXED: incorrect behavior of functions.norm() for non-complex arguments.

* FIXED: undefined variable in functions.exp() template (reported by Thibault North).

* FIXED: inconsistent block/grid shapes in static kernels


0.2.4 (11 May 2013)
===================

* ADDED: ability to introduce new scalar arguments for nested computations
  (the API is quite ugly at the moment).

* FIXED: handling prefixes properly when connecting transformations to nested computations.

* FIXED: bug in dependency inference algorithm which caused it to ignore allocations in nested computations.


0.2.3 (25 Apr 2013)
===================

* ADDED: explicit :py:meth:`~reikna.cluda.api.Thread.release` (primarily for certain rare CUDA use cases).

* CHANGED: CLUDA API discovery interface (see the documentation).

* CHANGED: The part of CLUDA API that is supposed to be used by other layers was moved to the ``__init__.py``.

* CHANGED: CLUDA ``Context`` was renamed to ``Thread``, to avoid confusion with ``PyCUDA``/``PyOpenCL`` contexts.

* CHANGED: signature of :py:meth:`~reikna.cluda.api.Thread.create`; it can filter devices now, and supports interactive mode.

* CHANGED: :py:class:`~reikna.cluda.Module` with ``snippet=True`` is now :py:class:`~reikna.cluda.Snippet`

* FIXED: added ``transformation.mako`` and ``cbrng_ref.py`` to the distribution package.

* FIXED: incorrect parameter generation in ``test/cluda/cluda_vsizes/ids``.

* FIXED: skipping testcases with incompatible parameters in ``test/cluda/cluda_vsizes/ids`` and ``sizes``.

* FIXED: setting the correct length of :py:attr:`~reikna.cluda.api.DeviceParameters.max_num_groups` in case of CUDA and a device with CC < 2.

* FIXED: typo in ``cluda.api_discovery``.


0.2.2 (20 Apr 2013)
===================

* ADDED: ability to use custom argument names in transformations.

* ADDED: multi-argument :py:func:`~reikna.cluda.functions.mul`.

* ADDED: counter-based random number generator :py:class:`~reikna.cbrng.CBRNG`.

* ADDED: ``reikna.elementwise.Elementwise`` now supports argument dependencies.

* ADDED: Module support in CLUDA; see :ref:`tutorial-modules` for details.

* ADDED: :py:func:`~reikna.helpers.template_def`.

* CHANGED: ``reikna.cluda.kernel.render_template_source`` is the main renderer now.

* CHANGED: ``FuncCollector`` class was removed; functions are now used as common modules.

* CHANGED: all templates created with :py:func:`~reikna.helpers.template_for` are now rendered with ``from __future__ import division``.

* CHANGED: signature of ``OperationRecorder.add_kernel`` takes a renderable instead of a full template.

* CHANGED: :py:meth:`~reikna.cluda.api.Thread.compile_static` now takes a template instead of a source.

* CHANGED: ``reikna.elementwise.Elementwise`` now uses modules.

* FIXED: potential problem with local size finidng in static kernels (first approximation for the maximum workgroup size was not that good)

* FIXED: some OpenCL compilation warnings caused by an incorrect version querying macro.

* FIXED: bug with incorrect processing of scalar global size in static kernels.

* FIXED: bug in variance estimates in CBRNG tests.

* FIXED: error in the temporary varaiable type in :py:func:`reikna.cluda.functions.polar` and :py:func:`reikna.cluda.functions.exp`.


0.2.1 (8 Mar 2013)
==================

* FIXED: function names for kernel ``polar()``, ``exp()`` and ``conj()``.

* FIXED: added forgotten kernel ``norm()`` handler.

* FIXED: bug in ``Py.Test`` testcase execution hook which caused every test to run twice.

* FIXED: bug in nested computation processing for computation with more than one kernel.

* FIXED: added dependencies between :py:class:`~reikna.matrixmul.MatrixMul` kernel arguments.

* FIXED: taking into account dependencies between input and output arrays as well as the ones
  between internal allocations --- necessary for nested computations.

* ADDED: discrete harmonic transform :py:class:`~reikna.dht.DHT`
  (calculated using Gauss-Hermite quadrature).


0.2.0 (3 Mar 2013)
==================

* Added FFT computation (slightly optimized PyFFT version + Bluestein's algorithm for non-power-of-2 FFT sizes)

* Added Python 3 compatibility

* Added Thread-global automatic memory packing

* Added polar(), conj() and exp() functions to kernel toolbox

* Changed name because of the clash with `another Tigger <http://www.astron.nl/meqwiki/Tigger>`_.


0.1.0 (12 Sep 2012)
===================

* Lots of changes in the API

* Added elementwise, reduction and transposition computations

* Extended API reference and added topical guides


0.0.1 (22 Jul 2012)
===================

* Created basic core for computations and transformations

* Added matrix multiplication computation

* Created basic documentation
