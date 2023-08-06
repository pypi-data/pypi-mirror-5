# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging
import warnings
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module
from concurrency.exceptions import RecordModifiedError

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def deprecated(replacement=None, version=None):
    """A decorator which can be used to mark functions as deprecated.
    replacement is a callable that will be called with the same args
    as the decorated function.

    >>> @deprecated()
    ... def foo(x):
    ...     return x
    ...
    >>> ret = foo(1)
    DeprecationWarning: foo is deprecated
    >>> ret
    1
    >>>
    >>>
    >>> def newfun(x):
    ...     return 0
    ...
    >>> @deprecated(newfun)
    ... def foo(x):
    ...     return x
    ...
    >>> ret = foo(1)
    DeprecationWarning: foo is deprecated; use newfun instead
    >>> ret
    0
    >>>
    """
    def outer(oldfun):  # pragma: no cover
        def inner(*args, **kwargs):
            msg = "%s is deprecated" % oldfun.__name__
            if version is not None:
                msg += "will be removed in version %s;" % version
            if replacement is not None:
                msg += "; use %s instead" % (replacement)
            warnings.warn(msg, DeprecationWarning, stacklevel=2)
            if callable(replacement):
                return replacement(*args, **kwargs)
            else:
                return oldfun(*args, **kwargs)
        return inner
    return outer


class ConcurrencyTestMixin(object):
    """
    Mixin class to test Models that use `VersionField`

    this class offer a simple test scenario. Its purpose is to discover
    some conflict in the `save()` inheritance::

        from concurrency.utils import ConcurrencyTestMixin
        from myproject.models import MyModel

        class MyModelTest(ConcurrencyTestMixin, TestCase):
            concurrency_model = TestModel0
            concurrency_kwargs = {'username': 'test'}

    """

    concurrency_model = None
    concurrency_kwargs = {}

    def _get_concurrency_target(self, **kwargs):
        # WARNING this method must be idempotent. ie must returns
        # always a fresh copy of the record
        args = dict(self.concurrency_kwargs)
        args.update(kwargs)
        return self.concurrency_model.objects.get_or_create(**args)[0]

    def test_concurrency_conflict(self):
        import concurrency.api as api
        target = self._get_concurrency_target()
        target_copy = self._get_concurrency_target()
        v1 = api.get_revision_of_object(target)
        v2 = api.get_revision_of_object(target_copy)
        assert v1 == v2, "got same row with different version (%s/%s)" % (v1, v2)
        target.save()
        assert target.pk is not None  # sanity check
        self.assertRaises(RecordModifiedError, target_copy.save)

    def test_concurrency_safety(self):
        import concurrency.api as api
        target = self.concurrency_model()
        version = api.get_revision_of_object(target)
        self.assertFalse(bool(version), "version is not null %s" % version)

    def test_concurrency_management(self):
        target = self.concurrency_model
        self.assertTrue(hasattr(target, 'RevisionMetaInfo'),
                        "%s is not under concurrency management" % self.concurrency_model)
        info = getattr(target, 'RevisionMetaInfo', None)
        revision_field = info.field

        self.assertTrue(revision_field in target._meta.fields,
                        "%s: version field not in meta.fields" % self.concurrency_model)


class ConcurrencyAdminTestMixin(object):
    pass


# def import_by_path(dotted_path, error_prefix=''):
#     """
#     Import a dotted module path and return the attribute/class designated by the
#     last name in the path. Raise ImproperlyConfigured if something goes wrong.
#     """
#     try:
#         module_path, class_name = dotted_path.rsplit('.', 1)
#     except ValueError:
#         raise ImproperlyConfigured("%s%s doesn't look like a module path" % (
#             error_prefix, dotted_path))
#     try:
#         module = import_module(module_path)
#     except ImportError as e:
#         raise ImproperlyConfigured('%sError importing module %s: "%s"' % (
#             error_prefix, module_path, e))
#     try:
#         attr = getattr(module, class_name)
#     except AttributeError:
#         raise ImproperlyConfigured('%sModule "%s" does not define a "%s" attribute/class' % (
#             error_prefix, module_path, class_name))
#     return attr
