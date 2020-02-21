import pymel.core as pm

from ..classes import AbstractRigModule
from ..utils.node import constrainTargets, createControlCurve, createNodeChain, createOffset
from ..utils.attribute import createVisibilitySwitch, lockRotate, lockScale, lockTranslate, remapAttr


class RigModule(AbstractRigModule):

    @property
    def module_type(self):
        return 'Limb'

    @classmethod
    def getOptionalParamNames(cls):
        return ('fk_ctrls', 'ik_ctrls')

    def build(self):

        # Bind specification parameters to locals
        name = self.spec['name']
        side = self.spec['side']
        color = self.spec['color']
        nodes = self.spec['nodes']
        scale = self.spec['scale']

        # Build target transforms and root
        self.buildTargets()

        # Build controls if necessary
        fk_ctrls = self.spec.get('fk_ctrls') or [
            createControlCurve('Fk_'+node.name(),
                               size=scale*0.8,
                               color=color)
            for node in nodes
        ]
        ik_ctrls = self.spec.get('ik_ctrls') or [
            createControlCurve('Ik_'+name+side,
                               ctrl_type='ik',
                               size=scale,
                               color=color),
            createControlCurve('Pv_'+name+side,
                               ctrl_type='pole',
                               size=scale/4.0,
                               color=color),
        ]

        # Build RigUnits
        fk_unit = self.buildFkChain(nodes,
                                    ctrls=fk_ctrls,
                                    name=name+side)
        ik_unit = self.buildIk2Bone(nodes,
                                    ctrls=ik_ctrls,
                                    name=name+side)

        _, cons_attrs = constrainTargets(
            zip(fk_unit.drivers, ik_unit.drivers), self.targets)

        # Add keyable attrs to root
        pm.addAttr(self.root, ln='ik_weight', at='float',
                   k=True, min=0.0, max=1.0, dv=1.0)
        rev_attr = remapAttr(self.root.ik_weight, out_range=(1.0, 0.0))
        drv_attrs = [rev_attr, self.root.ik_weight]

        for i in range(2):
            for cons_attr in cons_attrs:
                drv_attrs[i].connect(cons_attr[i])

        createVisibilitySwitch(self.root.ik_weight, ik_ctrls)
        createVisibilitySwitch(rev_attr, fk_ctrls)

        ik_ctrls[1].getParent().setParent(ik_ctrls[0])

        # Lock control channels
        lockTranslate(fk_ctrls)
        lockRotate(ik_ctrls[1])
        lockScale(fk_ctrls + ik_ctrls)

        for unit in fk_unit, ik_unit:
            unit.root.setParent(self.root)
