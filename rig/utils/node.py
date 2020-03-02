from functools import partial

import pymel.core as pm
import pymel.core.nodetypes as nt
from ...etc import CONTROL_SHAPES

CONTROL_COLORS = {
    '_l': (0, 0, 1),
    '_r': (1, 0, 0),
    '_m': (1, 1, 0)
}


def getRelativeTransform(xform, parent):

    return xform.worldMatrix.get()*parent.worldInverseMatrix.get()


def synthConstraint(drivers, target):
    '''
    Returns blend weight attributes, if any (empty if len(drivers)==1)
    '''
    if not (isinstance(drivers, (list, tuple)) and target):
        pm.warning('synthConstraint: Invalid input: {}.'.format(
            [drivers, target]))
        return

    mults = list()
    for driver in drivers:
        mult = pm.createNode('multMatrix', name=driver.name() + '_MULT')
        mult.matrixIn[0].set(getRelativeTransform(target, driver))
        pm.connectAttr(driver.worldMatrix, mult.matrixIn[1])
        mults.append(mult)

    blend = pm.createNode('blendMatrix', name=target.name() + '_BLEND')
    pm.connectAttr(mults[0].matrixSum, blend.inputMatrix)
    weights = list()
    for i in range(1, len(drivers)):
        pm.connectAttr(mults[i].matrixSum, blend.target[i].targetMatrix)
        weights.append(blend.target[i].weight)

    outmult = pm.createNode('multMatrix', name=target.name() + '_MULT')
    outmult.matrixIn[0].set(target.inverseMatrix.get())
    pm.connectAttr(blend.outputMatrix, outmult.matrixIn[1])
    if target.getParent():
        pm.connectAttr(target.getParent().worldInverseMatrix,
                       outmult.matrixIn[2])

    pm.connectAttr(outmult.matrixSum, target.offsetParentMatrix, force=True)

    return weights


def constrainTargets(drivers, targets, constraint_func=pm.orientConstraint, maintainOffset=True):
    print('Constraining targets...')
    drivers = tuple(drivers)
    targets = tuple(targets)
    print('Drivers: {}'.format(drivers))
    print('Targets: {}'.format(tuple(targets)))
    return [constraint_func(drv, tgt, mo=maintainOffset)
            for drv, tgt in zip(drivers, targets)]


def createConnectorCurve(xforms, parent=None, name=None):
    xforms = pm.ls(xforms)

    if (len(xforms) < 2) or not all(isinstance(xform, pm.nodetypes.Transform) for xform in xforms):
        raise ValueError(
            'createConnectorCurve requires at least 2 transforms.')

    name = name or '{}_connector'.format(xforms[0].name())

    crv = pm.curve(name=name, ep=[xform.getTranslation(
        ws=True) for xform in xforms], d=1)
    crv.overrideEnabled.set(True)
    crv.overrideDisplayType.set(1)
    crv.setParent(parent)

    for i, xform in enumerate(xforms):
        loc = pm.pointCurveConstraint(crv.ep[i])[0]
        loc = pm.ls(loc)[0]
        pm.rename(loc, '{}_loc1'.format(xform.name()))
        pm.xform(loc, cp=True)
        pm.parentConstraint(xform, loc)
        loc.setParent(parent)
        loc.visibility.set(False)

    pm.select(None)

    return crv


def createControlCurve(name=None,
                       shape='FK',
                       size=1.0,
                       color=None):
    """
    Creates a curve using predefined parameters.

    Parameters
    ----------
    name : str
        Desired curve name in Maya
    ctrlType : str
        Shape type, as defined in rig.ControlShapes (the default is 'FK')
    size : float
        Curve radius, in Maya scene units (the default is 1.0)
    color : tuple
        Tuple of RGB values in 0.0 to 1.0 range.  Set to None to use Maya's default color.

    """

    shape_args = CONTROL_SHAPES.get(
        shape.lower(), CONTROL_SHAPES['fk'])

    if name:
        shape_args.update({'name': name})
        if not color:
            color = CONTROL_COLORS.get(name[-2:].lower(), None)

    crv = pm.curve(**shape_args)

    setColor(crv, color)
    crv.setScale([size, size, size])
    pm.makeIdentity(crv, apply=True)

    return crv


def createNodeChain(xform_list,
                    node_func=partial(pm.createNode, 'transform'),
                    name_list=None,
                    prefix='_'):

    xform_list = pm.ls(xform_list)

    if not name_list:
        name_list = [prefix + node.nodeName() for node in xform_list]

    node_list = list()
    for node, node_name in zip(xform_list, name_list):
        new_node = node_func(name=node_name)
        pm.delete(pm.parentConstraint(node, new_node))
        if node_list:
            new_node.setParent(node_list[-1])
        node_list.append(new_node)

    return node_list


def createOffset(node, name=None):
    node = pm.ls(node)[0]
    if isTransform(node, raise_error=True):
        parent = node.getParent()
        name = name or '{}_offset'.format(node.name())

        offset = pm.createNode('transform', name=name)
        copyMatrix(node, offset).setParent(parent).addChild(node)

        return offset


def copyMatrix(from_node, to_node, worldSpace=True):
    to_node.setMatrix(from_node.getMatrix(ws=worldSpace), ws=worldSpace)
    return to_node


def getNodeTree(nodes, indices=True):
    nodes = [pm.ls(node)[0] for node in nodes]

    node_tree = {node: node.getParent() for node in nodes}

    if indices:
        def getIdx(x):
            return nodes.index(x) if x in nodes else None

        return {getIdx(k): getIdx(v) for k, v in node_tree.items()}

    return node_tree


def isTransform(node, raise_error=False):
    is_xform = isinstance(node, nt.Transform)

    if not is_xform:
        if raise_error:
            raise TypeError(
                'Node {} is not of type "Transform".'.format(str(node)))
        else:
            return False

    return True


def setColor(node, color=None):

    node = pm.ls(node)
    if not node:
        return
    else:
        node = node[0]

    if color is None:
        node.overrideEnabled.set(False)
        return

    node.overrideEnabled.set(True)

    use_index = isinstance(color, int)
    node.overrideRGBColors.set(not use_index)

    if use_index:
        node.overrideColor.set(color)
    else:
        node.overrideColorRGB.set(color)

    return
