"""Cases for `custom_features.ipynb`."""

from types import SimpleNamespace

from pandas.testing import assert_index_equal


def case_cols(ns: SimpleNamespace):
    assert_index_equal(ns.objects.columns, ns.my_objects.columns)
