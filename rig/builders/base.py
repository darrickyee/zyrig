from functools import wraps

import pymel.core as pm

from ..utils import isTransform


def builder(min_xforms=1, max_xforms=10, output_keys=('name', 'unit_type',  'root', 'controls', 'drivers', 'targets')):
    """Decorator for validation of builder input and output.
    1. Checks that input xforms satisfy mins and maxes specified by `min_xforms` and `max_xforms`.
    2. Enables specifying `xforms` as nodes or string names.
    3. Ensures output has all keys specified in `output_keys`.
    """

    def builderDecorator(func):

        @wraps(func)
        def builderWrapper(xforms, *args, **kwargs):

            xforms = pm.ls(xforms)

            # Validate xform types and counts
            if len(xforms) < min_xforms:
                raise ValueError(
                    "'{0}' requires at least {1} input transforms.".format(
                        func.__name__, min_xforms))

            if len(xforms) > max_xforms:
                raise ValueError(
                    "'{0}' requires no more than {1} input transforms.".format(
                        func.__name__, max_xforms))

            if not all(isTransform(xform) for xform in xforms):
                raise TypeError("{}: 'xforms' must consist of Transform nodes or names.".format(
                    func.__name__))

            unit = func(xforms, *args, **kwargs)

            if not isinstance(unit, dict):
                raise TypeError("{0}: Incorrect return type for builder function (got {1}, expected 'dict').".format(
                    func.__name__, type(unit)))

            if not all(k in unit for k in output_keys):
                raise KeyError("{0}: Improper output for rig unit: Expected keys: {1}, found {2}.".format(
                    func.__name__, output_keys, tuple(unit.keys())))

            return unit

        return builderWrapper

    return builderDecorator
