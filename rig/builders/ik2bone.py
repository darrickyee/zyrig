import pymel.core as pm

from ..utils import createControlCurve, createOffset, getPoleVector, createConnectorCurve, freezeOffset
from .base import builder
from .ikchain import buildUnit as buildIkChain


@builder(min_xforms=3, max_xforms=3)
def buildUnit(xforms, name=None, **kwargs):

    unit = buildIkChain(xforms, name, size=kwargs.get(
        'size', 8.0), color=kwargs.get('color', None))

    unit['name'] = name or 'Ik2Bone'
    unit['unit_type'] = 'ik2Bone'
    unit['xforms'] = unit['targets']

    unit.update(kwargs)

    unit['controls'] = _buildControls(**unit)
    unit['drivers'] = _buildDrivers(**unit)

    return _finalize(**unit)


def _buildControls(name, xforms, controls, pole_shape='Pole', polesize=3.0, color=None, **kwargs):
    pole = createControlCurve(name='Pv_{}'.format(
        name), shape=pole_shape, size=polesize, color=color)

    createOffset(pole)

    crv = createConnectorCurve((xforms[1], pole), parent=controls[0])

    pole.visibility.connect(crv.visibility)

    return [controls[0], pole]


def _buildDrivers(xforms, controls, root, drivers, pole_offset=50.0, **kwargs):
    # Position pole vector control
    pole_xf = controls[1].getParent()
    pole_xf.setTranslation(xforms[1].getTranslation(
        space='world') + getPoleVector(*xforms).normal()*pole_offset, space='world')

    # Apply pole vector constraint to ik handle
    ikh = root.listRelatives(ad=True, type='ikHandle')[0]
    pm.poleVectorConstraint(controls[1], ikh)

    return drivers


def _finalize(name, unit_type, controls, drivers, xforms, root, **kwargs):

    controls[1].getParent().setParent(controls[0])

    pm.select(None)

    return {'name': name,
            'unit_type': unit_type,
            'controls': controls,
            'drivers': drivers,
            'targets': xforms,
            'root': root}
