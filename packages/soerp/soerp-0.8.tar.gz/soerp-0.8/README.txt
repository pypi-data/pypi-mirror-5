Overview
=========

``soerp`` is the Python implementation of the original Fortran code `SOERP` by N. D. Cox to apply a second-order analysis to `error propagation`_ (or uncertainty analysis). The ``soerp`` package allows you to **easily** and **transparently** track the effects of uncertainty through mathematical calculations. Advanced mathematical functions, similar to those in the standard `math`_ module can also be evaluated directly.

In order to correctly use ``soerp``, knowledge of the **first eight statistical moments** is required. These are the *mean*, *variance*, and then the *standardized third through eighth moments*. These can be input manually in the form of an array, but they can also be **conveniently generated** using distributions from the ``scipy.stats`` sub-module. See the examples below for usage examples of both input methods. The result of all calculations generates a *mean*, *variance*, and *standardized skewness and kurtosis* coefficients.


Required Packages
=================

- `ad`_ : For automatic differentiation (install this first).

Suggested Packages
==================

- `SciPy`_ : Scientific Python
- `uncertainties`_ : First-order uncertainty propagation

Basic examples
==============
::

    >>> from soerp import uv   # the constructor for uncertain variables

    >>> x1 = uv([24, 1, 0, 3, 0, 15, 0, 105])  # normally distributed
    >>> x2 = uv([37, 16, 0, 3, 0, 15, 0, 105])  # normally distributed
    >>> x3 = uv([0.5, 0.25, 2, 9, 44, 265, 1854, 14833])  # exponentially distributed

    >>> Z = (x1*x2**2)/(15*(1.5 + x3))
    >>> Z  # output compactly shows the mean, variance, and standardized skewness and kurtosis
    UF(1176.45, 99699.6822919, 0.708013052954, 6.16324345122)

    >>> print Z  # explicitly calling print shows more detailed output
    UncertainFunction:
     > Mean...................  1176.45
     > Variance...............  99699.6822917
     > Skewness Coefficient...  0.708013052944
     > Kurtosis Coefficient...  6.16328545042
        
    >>> import scipy.stats as ss   # using empirically defined distribution objects
    >>> x1 = uv(rv=ss.norm(loc=24, scale=1))  # normally distributed
    >>> x2 = uv(rv=ss.norm(loc=37, scale=4))  # normally distributed
    >>> x3 = uv(rv=ss.expon(scale=0.5))  # exponentially distributed
    
    >>> x1.moments  # the eight moments can be accessed at any time
    [24.0, 1.0, 0.0, 3.0000000000000053, 0.0, 15.000000000000004, 0.0, 105.0]
    
    >>> x1-x1  # correlations are correctly handled
    UF(0.0, 0.0, 0.0, 0.0)
    
    # convenient access to derivatives
    >>> Z.d(x1)  # first derivative wrt x1 (returns all if no input, 0 if derivative doesn't exist)
    45.63333333333333

    >>> Z.d2(x2)  # second derivative wrt x2
    1.6

    >>> Z.d2c(x1, x3)  # second cross-derivative wrt x1 and x3 (order doesn't matter)
    -22.816666666666666
    
    >>> Z.gradient([x1, x2, x3])  # convenience function, useful for optimization
    [45.63333333333333, 59.199999999999996, -547.6]

    >>> Z.hessian([x1, x2, x3])   # another convenience function
    [[0.0, 2.466666666666667, -22.816666666666666], [2.466666666666667, 1.6, -29.6], [-22.816666666666666, -29.6, 547.6]]

    >>> Z.error_components(pprint=True)  # show how each variable is contributing errors
    *****************************************************************
    COMPOSITE VARIABLE ERROR COMPONENTS
    norm(24.0, 1.0, 0.0, 3.0) = 2196.15170139 or 2.202767%
    norm(37.0, 16.0, 0.0, 3.0) = 58202.9155556 or 58.378236%
    expon(0.5, 0.25, 2.0, 9.0) = -35665.8249653 or 35.773258%
    
    # a more advanced example
    >>> from soerp.umath import *  # sin, exp, sqrt, etc.
    >>> print '*'*80
    >>> print 'Example of volumetric gas flow through orifice meter'
    >>> H = uv(rv=ss.norm(loc=64, scale=0.5))
    >>> M = uv(rv=ss.norm(loc=16, scale=0.1))
    >>> P = uv(rv=ss.norm(loc=361, scale=2))
    >>> t = uv(rv=ss.norm(loc=165, scale=0.5))
    >>> C = 38.4
    >>> Q = C*umath.sqrt((520*H*P)/(M*(t + 460)))
    
    >>> print Q
    UncertainFunction:
     > Mean...................  1330.99973939
     > Variance...............  58.210762839
     > Skewness Coefficient...  0.0109422068056
     > Kurtosis Coefficient...  3.00032692988
    
Main Features
=============

1. **Transparent calculations** with derivatives automatically calculated. **No or little modification** to existing code required.
2. Basic `NumPy` support without modification. Vectorized calculations built-in to the ``ad`` package.
3. Nearly all standard `math`_ module functions supported through the ``soerp.umath`` sub-module. If you think a function is in there, it probably is.
4. Nearly all derivatives calculated analytically using ``ad`` functionality.

Installation
============

**Make sure you install the** `ad`_ **package first!**

You have several easy, convenient options to install the ``soerp`` package 
(administrative privileges may be required)

1. Download the package files below, unzip to any directory, and run ``python setup.py install`` from the command-line
2. Simply copy the unzipped ``soerp-XYZ`` directory to any other location that python can find it and rename it ``soerp``
3. If ``setuptools`` is installed, run ``easy_install --upgrade soerp`` from the command-line
4. If ``pip`` is installed, run ``pip --upgrade soerp`` from the command-line

Contact
=======

Please send **feature requests, bug reports, or feedback** to 
`Abraham Lee`_.

References
==========

- N.D. Cox, 1979, Tolerance Analysis by Computer, Journal of Quality Technology, Vol. 11, No. 2, pp. 80-87

Version History
===============

Main changes:

- 0.8: First public release.
  


.. _error propagation: http://en.wikipedia.org/wiki/Propagation_of_uncertainty
.. _math: http://docs.python.org/library/math.html
.. _ad: http://pypi.python.org/pypi/ad
.. _SciPy: http://scipy.org
.. _uncertainties: http://pypi.python.org/pypi/uncertainties
.. _Abraham Lee: mailto: tisimst@gmail.com
