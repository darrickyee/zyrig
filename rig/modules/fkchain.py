import pymel.core as pm

from ..classes import AbstractRigModule
from ..utils.node import constrainTargets, createControlCurve, createNodeChain, createOffset


class RigModule(AbstractRigModule):

    @property
    def module_type(self):
        return 'Finger'

    @classmethod
    def getOptionalParamNames(cls):
        return ('fkctrls')

    def build(self):

        # Bind specification parameters to locals
        name = self.spec['name']
        side = self.spec['side']
        color = self.spec['color']
        nodes = self.spec['nodes']
        scale = self.spec['scale']

        # Build controls if necessary
        fk_ctrls = self.spec.get('fk_ctrls') or [
            createControlCurve('Fk_'+node.name(),
                               size=scale,
                               color=color)
            for node in nodes
        ]

        # Build rig units
        fk_unit = self.buildFkChain(nodes,
                                    ctrls=fk_ctrls,
                                    name=name+side)

        constrainTargets(fk_unit.drivers, self.targets)
