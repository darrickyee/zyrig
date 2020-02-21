import importlib


def getModule(name):

    module_mod = importlib.import_module('zyrig.rig.modules.'+name)
    if hasattr(module_mod, 'RigModule'):
        module_mod.RigModule.__name__ = name
        return module_mod.RigModule

    raise ValueError("No RigModule named {}".format(name))

# Module tasks:
#   Build units
#   