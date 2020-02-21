import pymel.core as pm


def connectAttrMulti(src_attr, tgt_attrs):

    src_attr = pm.ls(src_attr)[0]
    tgt_attrs = pm.ls(tgt_attrs)

    for tgt in tgt_attrs:
        pm.connectAttr(src_attr, tgt)


def createVisibilitySwitch(driver_attr, on_nodes):
    driver_attr = pm.ls(driver_attr)[0]
    on_nodes = pm.ls(on_nodes)

    cond_node = pm.createNode(
        'condition', n='{}_vis'.format(driver_attr.nodeName()))
    cond_node.colorIfTrueR.set(1)
    cond_node.colorIfFalseR.set(0)
    cond_node.operation.set(2)

    pm.connectAttr(driver_attr, cond_node.firstTerm)
    for node in on_nodes:
        pm.connectAttr(cond_node.outColorR, node.visibility)


def makeLockXYZ(xf_name, unlock=False):

    def lockFunc(xforms):
        xforms = pm.ls(xforms)
        xf_attrs = [xf_name+axis for axis in ('X', 'Y', 'Z')]

        for xform in xforms:
            for xf_attr in xf_attrs:
                xform.attr(xf_attr).set(k=unlock, lock=not unlock)

    return lockFunc


def remapAttr(driver_attr, in_range=(0.0, 1.0), out_range=(0.0, 1.0)):

    driver_attr = pm.ls(driver_attr)[0]
    driver_attr.setRange(in_range)

    if tuple(in_range) == tuple(out_range):
        return driver_attr

    remap_node = pm.createNode(
        'remapValue', n='{}_remap1'.format(driver_attr.nodeName()))
    remap_node.inputMin.set(in_range[0])
    remap_node.inputMax.set(in_range[1])

    if out_range[0] > out_range[1]:
        remap_node.value[0].value_FloatValue.set(1)
        remap_node.value[1].value_FloatValue.set(0)

        out_range = tuple((out_range[1], out_range[0]))

    remap_node.outputMin.set(out_range[0])
    remap_node.outputMax.set(out_range[1])

    pm.connectAttr(driver_attr, remap_node.inputValue)

    return remap_node.outValue


def addWeightAttrs(attr_host, attr_name, constraints, defaultValue=0.0):
    '''
    First weight (index 0) gets full weight at `attr == 0`
    '''
    print('addWeightAttrs...')
    if any(len(constraint.getWeightAliasList()) < 2 for constraint in constraints):
        pm.warning(
            'addWeightAttr: Constraints must have at least 2 weight inputs.')
        return None

    attr_host = pm.ls(attr_host)[0]

    pm.addAttr(attr_host, ln=attr_name, at='float',
               minValue=0.0, maxValue=1.0, defaultValue=defaultValue, k=True)
    rev_attr = remapAttr(attr_host.attr(attr_name), out_range=(1.0, 0.0))

    connectAttrMulti(attr_host.attr(attr_name), [constraint.getWeightAliasList()[1]
                                                 for constraint in constraints])
    connectAttrMulti(rev_attr, [constraint.getWeightAliasList()[0]
                                for constraint in constraints])

    return (attr_host.attr(attr_name), rev_attr)


lockTranslate = makeLockXYZ('translate')
unlockTranslate = makeLockXYZ('translate', unlock=True)
lockRotate = makeLockXYZ('rotate')
unlockRotate = makeLockXYZ('rotate', unlock=True)
lockScale = makeLockXYZ('scale')
unlockScale = makeLockXYZ('scale', unlock=True)
