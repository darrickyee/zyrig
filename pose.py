import pymel.core as pm

arrow = {
    'point': ((0.0, 0.0, 0.0),
              (4.0, 0.0, 0.0),
              (4.0, 0.5, 0.0),
              (4.0, 0.0, 0.5),
              (4.0, -0.5, 0.0),
              (4.0, 0.0, -0.5),
              (4.0, 0.5, 0.0),
              (5.0, 0.0, 0.0),
              (4.0, 0.0, 0.5),
              (4.0, 0.0, -0.5),
              (5.0, 0.0, 0.0),
              (4.0, -0.5, 0.0),
              (4.0, 0.0, 0.0)),
    'degree': 1
}


def createPoseReader(target, angle=None, name=None, outerRadius=90.0, innerRadius=0.0):
    angle = angle or (0.0, 0.0, 0.0)
    if not name:
        suf = '_'.join(
            map(lambda p: p[0]+str(int(p[1])).replace('-', 'n'), zip(('x', 'y', 'z'), angle)))
        name = 'poseReader_' + target.nodeName() + '_' + suf

    # Create reader as curve
    reader = pm.curve(name=name, **arrow)
    reader.overrideEnabled.set(1)
    reader.overrideColor.set(3)

    # Position reader on target
    mult = pm.createNode('multMatrix', name=name+'_OFFSET')
    mult.matrixIn[0].set(target.xformMatrix.get())
    # Parent reader if target has parent
    parent = target.getParent()
    if parent:
        pm.connectAttr(parent.worldMatrix, mult.matrixIn[1])
    pm.connectAttr(mult.matrixSum, reader.offsetParentMatrix)

    # Create vectorProduct and angleBetween nodes
    ab = pm.createNode('angleBetween', name=name+'_ANGLE')
    vps = [pm.createNode('vectorProduct', name=name +
                         '_VEC{}'.format(i)) for i in range(2)]
    # Connect vps
    for src, vp in zip((reader, target), vps):
        vp.operation.set(3)
        vp.input1.set(1, 0, 0)
        pm.connectAttr(src.worldMatrix, vp.matrix)
        ab_in = 'vector1' if vp == vps[0] else 'vector2'
        pm.connectAttr(vp.output, ab.attr(ab_in))

    # Create remapValue
    rv = pm.createNode('remapValue', name=name+'_VALUE')
    for i in range(2):
        rv.value[i].value_FloatValue.set(1-i)

    # Create reader attributes
    pm.addAttr(reader, ln='outerRadius', at='float',
               maxValue=180.0, defaultValue=90.0, k=True)
    pm.addAttr(reader, ln='innerRadius', at='float', maxValue=180.0, k=True)
    pm.addAttr(reader, ln='poseWeight', at='float', k=True)

    # Connect angle & reader attributes
    pm.connectAttr(ab.angle, rv.inputValue)
    pm.connectAttr(reader.outerRadius, rv.inputMax)
    pm.connectAttr(reader.innerRadius, rv.inputMin)
    pm.connectAttr(rv.outValue, reader.poseWeight)

    # Rotate & set reader radius
    reader.outerRadius.set(pm.dt.Vector(angle).length())
    pm.rotate(reader, angle, r=True)

    pm.select(reader)


createPoseReader(pm.ls('Hip_R')[0], (0, -85, 0))
