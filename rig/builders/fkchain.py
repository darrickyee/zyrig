from ..utils import createControlCurve, createOffset, freezeOffset
from .base import builder


@builder()
def buildUnit(xforms, name=None, **kwargs):

    unit = {'name': name or 'FkChain',
            'unit_type': 'fkchain',
            'xforms': xforms}

    unit.update(kwargs)

    unit['controls'] = _buildControls(**unit)
    unit['drivers'] = _buildDrivers(**unit)

    return _finalize(**unit)


def _buildControls(xforms, shape='FK', size=5.0, color=None, **kwargs):

    return [createControlCurve(name='Fk_{0}'.format(xf.name()), shape=shape, size=size, color=color)
            for xf in xforms]


def _buildDrivers(controls, xforms, **kwargs):

    offsets = controls

    for i, offset in enumerate(offsets):
        offset.setTransformation(xforms[i].getMatrix(ws=True))

        if i:
            offset.setParent(controls[i-1])
            freezeOffset(offset)

    return controls


def _finalize(name, unit_type, controls, drivers, xforms, **kwargs):

    root = createOffset(controls[0], name='Fk_{}_GRP'.format(name))

    return {
        'name': name,
        'unit_type': unit_type,
        'controls': controls,
        'drivers': drivers,
        'targets': xforms,
        'root': root
    }
