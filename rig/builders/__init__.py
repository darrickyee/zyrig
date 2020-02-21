import importlib
from functools import wraps
import pymel.core as pm
from .base import builder

def getBuilder(name):

    builder_mod = importlib.import_module('zyrig.rig.builders.'+name)
    if hasattr(builder_mod, 'buildUnit'):
        builder_mod.buildUnit.__name__ = name
        return builder_mod.buildUnit

    raise ValueError("No RigUnit named {}.".format(name))
