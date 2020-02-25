from functools import partial, reduce

import pymel.core as pm

from ..utils import addWeightAttrs, createControlCurve, createNodeChain, createOffset, freezeOffset, synthConstraint
from .base import builder


@builder(min_xforms=3)
def buildUnit(xforms, name=None, **kwargs):

    unit = {
        'name': name or 'IkSpline',
        'unit_type': 'ikspline',
        'xforms': xforms
    }

    # Need to accommodate Python 2.7
    unit.update(kwargs)

    return reduce(lambda u, fn: fn(**u),
                  (_buildControls,
                   _buildSpline,
                   _attachControls,
                   _setRootHierarchy,
                   _connectControls,
                   _finalize),
                  unit)

############# Control-building functions #############


def _buildControls(name, shape='IK', size=15.0, color=None, **kwargs):

    return kwargs.update({'name': name,
                          'controls': [createControlCurve(name='Ik{0}_{1}'.format(pos+1, name),
                                                          shape=shape, size=size, color=color)
                                       for pos in range(3)]}
                         ) or kwargs

############# Spline-building functions #############


def _makeSplineJoints(xforms):
    joints = createNodeChain(xforms, node_func=partial(
        pm.createNode, 'joint'), prefix='iks_')

    for joint in joints:
        pm.makeIdentity(joint, apply=True)

    return joints


def _makeSplineCurve(xforms, name):
    return pm.rebuildCurve(pm.curve(name='iks_{}_crv'.format(name),
                                    ep=(xform.getTranslation(ws=True)
                                        for xform in xforms)), rt=0, spans=2)[0]


def _makeSplineIkHandle(joints, curve):
    ikh, _ = pm.ikHandle(ccv=False, curve=curve,
                         sj=joints[0], ee=joints[-1], solver='ikSplineSolver')

    return ikh


def _buildSpline(xforms, name, **kwargs):
    joints = _makeSplineJoints(xforms)
    curve = _makeSplineCurve(joints, name)
    ikh = _makeSplineIkHandle(joints, curve)

    pm.rename(ikh, '{}_ikHandle1'.format(name))

    return kwargs.update(
        {'name': name,
         'xforms': xforms,
         'joints': joints,
         'curve': curve,
         'ikhandle': ikh}
    ) or kwargs

############# Control-attachment functions #############


def _placeControls(controls, xforms, curve):

    controls[0].setTransformation(xforms[0].getMatrix(ws=True))
    controls[2].setTransformation(xforms[-1].getMatrix(ws=True))
    # Set mid control transform to "middle" of start and end
    controls[1].setTranslation(curve.getPointAtParam(
        curve.length()/2.0, space='world'), ws=True)
    pm.delete(pm.orientConstraint([controls[0], controls[2]], controls[1]))


def _attachControls(xforms, controls, curve, **kwargs):
    _placeControls(controls, xforms, curve)

    # Curve should have 5 cvs and there should be 3 controls
    clusters = [pm.cluster(cv)[1] for cv in curve.cv]
    for i in 0, 1:
        pm.parentConstraint(controls[0], clusters[i], mo=True)
    pm.parentConstraint(controls[1], clusters[2], mo=True)
    for i in -1, -2:
        pm.parentConstraint(controls[2], clusters[i], mo=True)

    return kwargs.update(
        {'xforms': xforms,
         'controls': controls,
         'curve': curve,
         'clusters': clusters}
    ) or kwargs


############# Control connection functions #############


def _setRootHierarchy(name, clusters, controls, curve, ikhandle, joints, **kwargs):
    print('Setting hierarchy...')
    root = createOffset(controls[0], name='Ik_{}_GRP'.format(name))
    for node in clusters + [ctrl for ctrl in controls] + [curve, ikhandle, joints[0]]:
        node.setParent(root)

    for node in clusters + joints + [curve, ikhandle]:
        node.visibility.set(0)

    curve.inheritsTransform.set(False)
    curve.setTransformation(pm.datatypes.Matrix())

    for ctrl in controls:
        freezeOffset(ctrl)

    return kwargs.update({
        'name': name,
        'controls': controls,
        'joints': joints,
        'root': root,
        'ikhandle': ikhandle}) or kwargs


def _makeCtrlConstraints(controls, joints, end_driver):
    # Create mid-control constraint
    mid = synthConstraint((controls[0], controls[2]), controls[1])
    # Create end-driver constraint
    end = synthConstraint((joints[-1], controls[2]), end_driver)
    return (mid, end)


def _addWeightAttrs(attr_host, wtattrs):
    print("adding weight attrs...")
    print(wtattrs)
    for attr_name, wtattr in zip(('midWeight', 'endWeight'), wtattrs):
        pm.addAttr(attr_host, ln=attr_name, at='float', minValue=0.0,
                   maxValue=1.0, defaultValue=0.5, k=True)
        pm.connectAttr(attr_host.attr(attr_name), wtattr[0], force=True)


def _addTwistControls(controls, ikhandle):
    ikhandle.dTwistControlEnable.set(True)
    ikhandle.dWorldUpType.set(4)
    controls[0].worldMatrix[0].connect(ikhandle.dWorldUpMatrix)
    controls[2].worldMatrix[0].connect(ikhandle.dWorldUpMatrixEnd)


def _connectControls(controls, joints, ikhandle, **kwargs):
    end_driver = createNodeChain(joints[-1],
                                 name_list=[joints[-1].name()+'_drv'])[0]
    end_driver.setParent(joints[-1])

    _addWeightAttrs(controls[2], _makeCtrlConstraints(
        controls, joints, end_driver))

    _addTwistControls(controls, ikhandle)

    print('Finishing connect controls...')
    return kwargs.update({
        'controls': controls,
        'joints': joints,
        'drivers': joints[:-1] + [end_driver]
    }) or kwargs


############# Finalization functions #############


def _finalize(**kwargs):

    pm.select(None)
    kwargs['targets'] = kwargs['xforms']

    print('Returning Ik Spline unit...')
    return {k: kwargs[k]
            for k in ('name',
                      'unit_type',
                      'root',
                      'controls',
                      'drivers',
                      'targets')}
