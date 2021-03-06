import pymel.core as pm

from ..utils import createNodeChain, createOffset, remapAttr
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

    return reduce(lambda unit, fn: fn(**unit), [_buildDrivers, _connectDrivers, _finalize], unit)


def alignAxis(xform, axis='x', target_axis=(1, 0, 0)):
    axidx = ['x', 'y', 'z'].index(axis.lower())
    mat = xform.getMatrix()
    angle = pm.angleBetween(v1=mat[axidx][:3], v2=target_axis, euler=True)
    pm.rotate(xform, angle, r=True, pcp=True)


def aimAxis(xform, target, axis='x'):
    alignAxis(xform, axis=axis, target_axis=target.getTranslation(
        space='world')-xform.getTranslation(space='world'))


def _buildDrivers(name, xforms, **kwargs):

    # Create reverse foot transforms
    heel, toe, ball, ankle = createNodeChain(xforms[::-1], prefix='rf_')
    ball_pivot = createNodeChain(ball, name_list=[ball.name()+'_pivot'])[0]
    ball_roll = createNodeChain(ball, name_list=[ball.name()+'_roll'])[0]

    aimAxis(heel, toe)
    alignAxis(heel, axis='y', target_axis=(0, 1, 0))
    alignAxis(ball_pivot, axis='y', target_axis=(0, 1, 0))

    ball_pivot.setParent(toe)
    ball.setParent(ball_pivot)
    ball_roll.setParent(ball_pivot)
    ankle.setParent(ball_roll)

    root = createNodeChain(xforms[0], name_list=['Rf_{}_GRP'.format(name)])[0]
    heel.setParent(root)

    for xform in root.listRelatives(ad=True, type='transform'):
        createOffset(xform)

    return kwargs.update({
        'name': name,
        'xforms': xforms,
        'root': root,
        'drivers': (ankle, ball),
        'roll_xforms': (heel, toe, ball_roll, ball_pivot)
    }) or kwargs


def _connectDrivers(root, roll_xforms, drivers, **kwargs):
    heel, toe, ball_roll, ball_pivot = roll_xforms

    for attr_name in 'roll', 'rollAngle', 'pivot', 'curl':

        pm.addAttr(root, ln=attr_name, at='float',
                   k=True, minValue=-90.0, maxValue=90.0,
                   defaultValue=(30.0 if attr_name == 'rollAngle' else 0.0))

    pm.connectAttr(root.pivot, ball_pivot.ry)
    pm.connectAttr(root.curl, drivers[1].rz)

    rev_angle = remapAttr(root.rollAngle, in_range=(
        0.0, 90.0), out_range=(0.0, -90.0))

    heel_attr = remapAttr(root.roll, in_range=(
        0.0, -90.0), out_range=(0.0, 90.0))
    pm.connectAttr(heel_attr, heel.rz)

    roll_attr = remapAttr(root.roll, in_range=(
        0.0, 30.0), out_range=(0.0, -30.0))
    pm.connectAttr(roll_attr, ball_roll.rz)
    pm.connectAttr(root.rollAngle, roll_attr.node().inputMax)
    pm.connectAttr(rev_angle, roll_attr.node().outputMin)

    toe_attr = remapAttr(root.roll, in_range=(
        30.0, 90.0), out_range=(0.0, -90.0))
    pm.connectAttr(toe_attr, toe.rz)
    pma = pm.createNode('plusMinusAverage', name=toe.name()+'_SUB')
    pma.operation.set(2)
    pma.input1D[0].set(-90)
    pm.connectAttr(rev_angle, pma.input1D[1])
    pm.connectAttr(root.rollAngle, toe_attr.node().inputMin)
    pm.connectAttr(pma.output1D, toe_attr.node().outputMin)

    return kwargs.update({
        'root': root,
        'drivers': drivers,
        'controls': []
    }) or kwargs


def _finalize(name, unit_type, controls, drivers, xforms, root, **kwargs):

    return {'name': name,
            'unit_type': unit_type,
            'controls': controls,
            'drivers': drivers,
            'targets': xforms[:2],
            'root': root}
