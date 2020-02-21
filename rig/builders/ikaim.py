from functools import partial

import pymel.core as pm

from ..utils import createControlCurve, createNodeChain, createOffset
from .base import builder

# pm.aimConstraint('locator1', 'Eye_L', mo=True, wut='objectrotation', wuo='locator1')


@builder(min_xforms=2)
def buildUnit(xforms, name=None, **kwargs):
    # xforms: 0 = constrained, 1 = constraint target

    unit = {'name': name or 'Aim',
            'unit_type': 'aim',
            'xforms': xforms}

    unit.update(kwargs)

    unit['controls'] = _buildControls(**unit)
    unit['drivers'] = _buildDrivers(**unit)

    return _finalize(**unit)


def _buildControls(name, shape='Aim', size=2.0, color=None, **kwargs):
    ctrl = createControlCurve(name='Aim_{}'.format(
        name), shape=shape, size=size, color=color)

    createOffset(ctrl)

    return [ctrl]


def _buildDrivers(controls, xforms, **kwargs):
    # Place control curve
    offset = controls[0].getParent()
    controls[0].getParent().setTransformation(xforms[-1].getMatrix(ws=True))

    ctrl_orient = kwargs.get('ctrl_orient', None)
    if ctrl_orient:
        pm.rotate(offset, ctrl_orient)

    driver = createNodeChain(xforms[0],
                             name_list=['Aim_' + xforms[0].name()+'_drv'])[0]

    pm.aimConstraint(controls[0], driver, mo=True,
                     wut='objectrotation', wuo=controls[0].name())

    return [driver]


def _finalize(name, controls, drivers, **kwargs):
    root = createOffset(controls[0].getParent(), name='Aim_{}_GRP'.format(name))
    controls[0].setParent(root)
    drivers[0].setParent(root)

    return {
        'root': root,
        'name': name,
        'controls': controls,
        'drivers': drivers,
        'targets': kwargs['xforms'],
        'unit_type': kwargs['unit_type']
    }
