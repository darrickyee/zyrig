from functools import partial

import pymel.core as pm

from ..utils import createControlCurve, createNodeChain, createOffset, freezeOffset
from .base import builder

# TODO: Figure out if controls are needed? (Toe curl?)
# TODO: Need access to ankle constraint?
@builder(min_xforms=4, max_xforms=4)
def buildUnit(xforms, name=None, **kwargs):
    # Ankle, ToeBall, ToeEnd, Heel
    unit = {
        'name': name or 'ReverseFoot',
        'unit_type': 'revfoot',
        'xforms': xforms,
        'targets': xforms[:4]
    }

    unit.update(kwargs)
    unit['drivers'] = _buildDrivers(**unit)

    return _finalize(**unit)


def _buildControls(name, shape='IK', size=5.0, color=None, **kwargs):

    return [createControlCurve(
        name='Ik_{}'.format(name), shape=shape, size=size, color=color)]


def _buildDrivers(xforms, **kwargs):

    # Create reverse foot joints
    joints = createNodeChain(xforms[::-1], node_func=partial(
        pm.createNode, 'joint'), prefix='rf_')
    for joint in joints:
        pm.makeIdentity(joint, apply=True)

    # Aim constraints for ankle and ball
    for i in range(2):
        # TODO: Fix up vector?
        pm.aimConstraint(joints[-2-i], joints[-1-i], mo=True,
                         wut='objectrotation', wuo=joints[-2-i].name())

    return joints[::-1]


def _finalize(name, unit_type, controls, drivers, xforms, **kwargs):

    root = createOffset(drivers[0], name='RevFoot_{}_GRP'.format(name))
    for node in drivers[0], controls[0]:
        node.setParent(root)

    freezeOffset(controls[0])

    return {'name': name,
            'unit_type': unit_type,
            'controls': controls,
            'drivers': drivers,
            'targets': xforms,
            'root': root}
