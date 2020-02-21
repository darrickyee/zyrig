from abc import ABCMeta, abstractmethod, abstractproperty

from ..builders import getBuilder
from ..utils import createNodeChain, createOffset


class AbstractRigModule(object):
    __metaclass__ = ABCMeta

    def __init__(self, module_spec):

        self.spec = module_spec
        self.validateInput()

        self.buildFkChain = getBuilder('fkchain')
        self.buildIkChain = getBuilder('ikchain')
        self.buildIk2Bone = getBuilder('ik2bone')
        self.buildIkSpline = getBuilder('ikspline')
        self.buildRevFoot = None
        self.buildAim = None

        self.targets = list()
        self.root = None

    @abstractproperty
    def module_type(self):
        pass

    @abstractmethod
    def build(self):
        pass

    @classmethod
    def getParamNames(cls):
        """Collection of parameter names required for building the module."""
        return (
            'name',
            'side',
            'color',
            'nodes',
            'scale'
        )

    @classmethod
    def getOptionalParamNames(self):
        """Optional parameter names."""
        return ()

    def buildTargets(self, nodes=None):
        nodes = nodes or self.spec['nodes']
        self.targets = createNodeChain(nodes, prefix='tgt_')
        self.root = createOffset(
            self.targets[0], name=self.spec['name']+self.spec['side']+'_GRP')

    def validateInput(self):
        """Check that required attributes are on the guide input object.

        Default implementation expects guide to be dict-like.  Override 
        this method to accommodate guides of another type."""

        for param in self.getParamNames():
            if param not in self.spec:
                raise KeyError(
                    "{0}: Required parameter '{1}' not found in module specification.".format(
                        type(self).__name__, param)
                )

        return True
