import numpy

import reikna.helpers as helpers
import reikna.cluda.dtypes as dtypes
from reikna.cluda import Module

TEMPLATE = helpers.template_for(__file__)


class Sampler:
    """
    Contains a random distribution sampler module and accompanying metadata.
    Supports ``__process_modules__`` protocol.

    .. py:attribute:: deterministic

        If ``True``, every sampled random number consumes the same amount of counters.

    .. py:attribute:: randoms_per_call

        How many random numbers one call to ``sample`` creates.

    .. py:attribute:: dtype

        The data type of one random value produced by the sampler.

    .. py:attribute:: module

        The module containing the distribution sampling function.
        It provides the C functions below.

    .. c:macro:: RANDOMS_PER_CALL

        Contains the value of :py:attr:`randoms_per_call`.

    .. c:type:: value

        Contains the type corresponding to :py:attr:`dtype`.

    .. c:type:: RESULT

        Describes the sampling result.

        .. c:member:: value v[RANDOMS_PER_CALL]

    .. c:type:: RESULT sample(STATE *state)

        Performs the sampling, updating the state.
    """
    def __init__(self, bijection, module, dtype, randoms_per_call=1, deterministic=False):
        """__init__()""" # hide the signature from Sphinx
        self.randoms_per_call = randoms_per_call
        self.dtype = dtypes.normalize_type(dtype)
        self.deterministic = deterministic
        self.bijection = bijection
        self.module = module

    def __process_modules__(self, process):
        return Sampler(
            process(self.bijection), process(self.module), self.dtype,
            randoms_per_call=self.randoms_per_call,
            deterministic=self.deterministic)


def uniform_integer(bijection, dtype, low, high=None):
    """
    Generates uniformly distributed integer numbers in the interval ``[low, high)``.
    If ``high`` is ``None``, the interval is ``[0, low)``.
    Supported dtypes: any numpy integers.
    If the size of the interval is a power of 2, a fixed number of counters
    is used in each thread.
    Returns a :py:class:`~reikna.cbrng.samplers.Sampler` object.
    """

    if high is None:
        low, high = 0, low + 1
    else:
        assert low < high - 1

    dtype = dtypes.normalize_type(dtype)
    ctype = dtypes.ctype(dtype)

    if dtype.kind == 'i':
        assert low >= -2 ** (dtype.itemsize * 8 - 1)
        assert high < 2 ** (dtype.itemsize * 8 - 1)
    else:
        assert low >= 0
        assert high < 2 ** (dtype.itemsize * 8)

    num = high - low
    if num <= 2 ** 32:
        raw_dtype = numpy.uint32
        raw_func = 'get_raw_uint32'
        max_num = 2 ** 32
    else:
        raw_dtype = numpy.uint64
        raw_func = 'get_raw_uint64'
        max_num = 2 ** 64
    raw_ctype = dtypes.ctype(dtypes.normalize_type(raw_dtype))

    module = Module(
        TEMPLATE.get_def("uniform_integer"),
        render_kwds=dict(
            bijection=bijection,
            dtype=dtype, ctype=ctype,
            raw_ctype=raw_ctype, raw_func=raw_func,
            max_num=max_num, num=num, low=low))

    return Sampler(bijection, module, dtype, deterministic=(max_num % num == 0))


def uniform_float(bijection, dtype, low=0, high=1):
    """
    Generates uniformly distributed floating-points numbers in the interval ``[low, high)``.
    Supported dtypes: ``float(32/64)``.
    A fixed number of counters is used in each thread.
    Returns a :py:class:`~reikna.cbrng.samplers.Sampler` object.
    """
    assert low < high

    ctype = dtypes.ctype(dtype)

    bitness = 64 if dtypes.is_double(dtype) else 32
    raw_func = 'get_raw_uint' + str(bitness)
    raw_max = dtypes.c_constant(2 ** bitness, dtype)

    size = dtypes.c_constant(high - low, dtype)
    low = dtypes.c_constant(low, dtype)

    module = Module(
        TEMPLATE.get_def("uniform_float"),
        render_kwds=dict(
            bijection=bijection, ctype=ctype,
            raw_func=raw_func, raw_max=raw_max, size=size, low=low))

    return Sampler(bijection, module, dtype, deterministic=True)


def normal_bm(bijection, dtype, mean=0, std=1):
    """
    Generates normally distributed random numbers with the mean ``mean`` and
    the standard deviation ``std`` using Box-Muller transform.
    Supported dtypes: ``float(32/64)``.
    Produces two random numbers per call.
    Returns a :py:class:`~reikna.cbrng.samplers.Sampler` object.
    """

    ctype = dtypes.ctype(dtype)
    uf = uniform_float(bijection, dtype, low=0, high=1)

    module = Module(
        TEMPLATE.get_def("normal_bm"),
        render_kwds=dict(
            dtype=dtype, ctype=ctype, bijection=bijection,
            mean=dtypes.c_constant(mean, dtype),
            std=dtypes.c_constant(std, dtype),
            uf=uf))

    return Sampler(
        bijection, module, dtype,
        deterministic=uf.deterministic, randoms_per_call=2)


def gamma(bijection, dtype, shape=1, scale=1):
    """
    Generates random numbers from the gamma distribution

    .. math::
      P(x) = x^{k-1} \\frac{e^{-x/\\theta}}{\\theta^k \\Gamma(k)},

    where :math:`k` is ``shape``, and :math:`\\theta` is ``scale``.
    Supported dtypes: ``float(32/64)``.
    Returns a :py:class:`~reikna.cbrng.samplers.Sampler` object.
    """

    ctype = dtypes.ctype(dtype)
    uf = uniform_float(bijection, dtype, low=0, high=1)
    nbm = normal_bm(bijection, dtype, mean=0, std=1)

    module = Module(
        TEMPLATE.get_def("gamma"),
        render_kwds=dict(
            dtype=dtype, ctype=ctype, bijection=bijection,
            shape=shape, scale=dtypes.c_constant(scale, dtype),
            uf=uf, nbm=nbm))

    return Sampler(bijection, module, dtype)


# List of samplers that can be used as convenience constructors in CBRNG class
SAMPLERS = {
    'uniform_integer': uniform_integer,
    'uniform_float': uniform_float,
    'normal_bm': normal_bm,
    'gamma': gamma}
