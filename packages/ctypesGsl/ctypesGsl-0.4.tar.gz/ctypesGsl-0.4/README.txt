ctypesGsl is a Python binding for the GSL library using the ctypes
package.  It is probably somewhat slower than pygsl but has other
advantages:

1. It is very easy to install, the only dependency (except for GSL
   itself) is the ctypes package, standard since Python 2.5.  No
   compilation or is required during installation.  The implementation
   is simpler too as it does not require SWIG wrappers, C code or
   shared libraries.

2. ctypes seems to be the preferred future way to do Python bindings,
   since it is independent from python implementation used, e.g. it
   should work with PyPy.

Currently it is slowly becoming reasonably complete.  Implemented are:

error handling
basic function
complex numbers
polynomials
special functions
vectors
matrices
permutations (incomplete)
combinations
BLAS
linear algebra
eigensystems
numerical integration
random number generators
quasi random number generators
probability distributions
Monte Carlo integration
ordinary differential equations
numerical integration
Chebyshev approximations
one dimensional root finding
one dimensional minimization
multidimensional root finding
multidimensional minimization


License
=======

GPL v.3, see LICENSE.txt


Installation
============

There is a (somewhat experimental) setup.py script in the top-level
directory.

Alternatively, just copy the ctypesGsl directory to

/usr/local/lib/python2.5/site-packages/

or wherever you keep your local python packages.  You're ready to go:

>>> import ctypesGsl
>>> ctypesGsl.expm1(1)
1.7182818284590451

the test_cgsl.py file contains some examples based on GSL tests.


Design
======

The idea is that the package should be usable like a standard python
library.  The low level functions are thus often wrapped in python
functions which try to hide some of the complexity.  

The higher level interface does error handling (exceptions are raised
if return value is not GSL_SUCCESS), and tries to make common usage
easy, e.g. gsl_complex numbers can be used just as standard Python
complex numbers, tries to allocate integration workspace of reasonable
size if none is provided, etc.

See the test_cgsl.py file for examples.


Error handling
==============

There are two ways to check for errors in GSL: internal error handler,
and return values.  ctypesGsl handles both.  The return values are
automatically checked and (by default) an exception is raised if the
return value indicates an error.

Unfortunately ctypes does not propagate exceptions raised inside
callback functions to the main thread, so if an exception is raised in
the internal error handler, a backtrace is printed but the program
continues.  Internal GSL error handler is thus (by default) redefined
to only print a warning message.

Both internal and return value error handlers can be redefined.


Documentation
=============

None at the moment.  See test_cgsl.py file for usage examples.
