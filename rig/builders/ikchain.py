from functools import partial

import pymel.core as pm

from ..utils import createControlCurve, createNodeChain, createOffset, freezeOffset
# from ..classes import RigUnit
from .base import builder


@builder(min_xforms=2)
def buildUnit(xforms, name=None, **kwargs):

    unit = {
        'name': name or 'IkChain',
        'unit_type': 'ikchain',
        'xforms': xforms
    }

    unit.update(kwargs)
    unit['controls'] = _buildControls(**unit)
    unit['drivers'] = _buildDrivers(**unit)

    return _finalize(**unit)


def _buildControls(name, shape='IK', size=5.0, color=None, **kwargs):

    return [createControlCurve(
        name='Ik_{}'.format(name), shape=shape, size=size, color=color)]


def _buildDrivers(name, xforms, controls, **kwargs):
    ctrl_orient = kwargs.get('ctrl_orient', None)

    # Create IK joints
    joints = createNodeChain(xforms, node_func=partial(
        pm.createNode, 'joint'), prefix='ikj_')
    for joint in joints:
        pm.makeIdentity(joint, apply=True)

    # Place control curve
    controls[0].setTransformation(xforms[-1].getMatrix(ws=True))

    if ctrl_orient:
        pm.rotate(controls[0], ctrl_orient)

    # Create IK chain
    ik_handle, _ = pm.ikHandle(n="Ik_{}_handle".format(name),
                               sj=joints[0], ee=joints[-1])
    ik_handle.setParent(controls[0])

    # Constrain end driver joint
    pm.orientConstraint(controls[0], joints[-1], mo=True)

    # Hide intermediate nodes
    for node in joints + [ik_handle]:
        node.visibility.set(False)

    return joints


def _finalize(name, unit_type, controls, drivers, xforms, **kwargs):

    root = createOffset(drivers[0], name='Ik_{}_GRP'.format(name))
    for node in drivers[0], controls[0]:
        node.setParent(root)
    
    freezeOffset(controls[0])

    return {'name': name,
            'unit_type': unit_type,
            'controls': controls,
            'drivers': drivers,
            'targets': xforms,
            'root': root}
