Changes
=======

.. currentmodule:: patsy

v0.2.1
------

* Fixed a nasty bug in missing value handling where, if missing values
  were present, ``dmatrix(..., result_type="dataframe")`` would always
  crash, and ``dmatrices("y ~ 1")`` would produce left- and right-hand
  side matrices that had different numbers of rows. (As far as I can
  tell, this bug could not possibly cause incorrect results, only
  crashes, since it always involved the creation of matrices with
  incommensurate shapes. Therefore there is no need to worry about the
  accuracy of any analyses that were successfully performed with
  v0.2.0.)
* Modified ``patsy/__init__.py`` to work around limitations in
  py2exe/py2app/etc.

v0.2.0
------

Warnings:

* The lowest officially supported Python version is now 2.5. So far as
  I know everything still works with Python 2.4, but as everyone else
  has continued to drop support for 2.4, testing on 2.4 has become so
  much trouble that I've given up.

New features:

* New support for automatically detecting and (optionally) removing
  missing values (see :class:`NAAction`).
* New stateful transform for B-spline regression:
  :func:`bs`. (Requires scipy.)
* Added a core API to make it possible to run predictions on only a
  subset of model terms. (This is particularly useful for
  e.g. plotting the isolated effect of a single fitted spline term.)
  See :meth:`DesignMatrixBuilder.subset`.
* :class:`LookupFactor` now allows users to mark variables as
  categorical directly.
* :class:`pandas.Categorical` objects are now recognized as
  representing categorical data and handled appropriately.
* Better error reporting for exceptions raised by user code inside
  formulas. We now, whenever possible, tag the generated exception
  with information about which factor's code raised it, and use this
  information to give better error reporting.
* :meth:`EvalEnvironment.capture` now takes a `reference` argument,
  to make it easier to implement new :func:`dmatrix`-like functions.

Other: miscellaneous doc improvements and bug fixes.

v0.1.0
------
  First public release.
