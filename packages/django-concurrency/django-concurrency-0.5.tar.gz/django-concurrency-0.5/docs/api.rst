.. include:: globals.rst

.. _api:

API
===

.. contents::
:local:

Forms
=====

ConcurrentForm
--------------
.. autoclass:: concurrency.forms.ConcurrentForm


VersionWidget
-------------
.. autoclass:: concurrency.forms.VersionWidget


Exceptions
==========

.. _VersionChangedError:

VersionChangedError
-------------------
.. autoclass:: concurrency.exceptions.VersionChangedError

.. _RecordModifiedError:

RecordModifiedError
-------------------
.. autoclass:: concurrency.exceptions.RecordModifiedError

.. _InconsistencyError:

InconsistencyError
-------------------
.. autoclass:: concurrency.exceptions.InconsistencyError


.. _VersionError:

VersionError
-------------------
.. autoclass:: concurrency.exceptions.VersionError


Helpers
=========

``concurrency_check()``
------------------------

Sometimes, VersionField(s) cannot wraps the save() method,
is these cirumstances you can check it manually ::

    from concurrency.core import concurrency_check

    class AbstractModelWithCustomSave(models.Model):
        version = IntegerVersionField(db_column='cm_version_id', manually=True)

    def save(self, *args, **kwargs):
        concurrency_check(self, *args, **kwargs)
        super(SecurityConcurrencyBaseModel, self).save(*args, **kwargs)

.. note:: Please note ``manually=True`` argument in `IntegerVersionField()` definition


.. _apply_concurrency_check:

``apply_concurrency_check()``
------------------------------
.. versionadded:: 0.4

Add concurrency check to existing classes.

.. autofunction:: concurrency.core.apply_concurrency_check


Test Utilties
=============

.. _ConcurrencyTestMixin:

ConcurrencyTestMixin
--------------------
.. autoclass:: concurrency.utils.ConcurrencyTestMixin


