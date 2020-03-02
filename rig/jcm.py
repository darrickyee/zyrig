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


def createPoseReader(target, rotation=None, name=None, outerRadius=90.0, innerRadius=0.0):
    target = pm.ls(target)[0]
    rotation = rotation or (0.0, 0.0, 0.0)
    if not name:
        suf = '_'.join(
            map(lambda p: p[0]+str(int(p[1])).replace('-', 'n'), zip(('x', 'y', 'z'), rotation)))
        name = 'poseReader_' + target.nodeName() + '_' + suf

    # Create reader as curve
    reader = pm.curve(name=name, **arrow)
    reader.overrideEnabled.set(1)
    reader.overrideColor.set(3)

    # Position reader on target
    offset = pm.createNode('transform', name='{}_offset'.format(reader.name()))
    offset.setMatrix(target.getMatrix(ws=True), ws=True)
    reader.setParent(offset)
    reader.setMatrix(pm.dt.Matrix())

    # Parent reader if target has parent
    parent = target.getParent()
    if parent:
        pm.parentConstraint(parent, offset, mo=True)

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

    # Rotate
    reader.outerRadius.set(outerRadius)
    reader.innerRadius.set(innerRadius)
    reader.outerRadius.set(pm.dt.Vector(rotation).length())
    pm.rotate(reader, rotation, r=True)

    pm.select(reader)

    return reader


JCMSALL = {'JCM_CollarUp_55_L': {},
           'JCM_CollarUp_55_R': {},
           'JCM_ForeArmFwd_135_L': {},
           'JCM_ForeArmFwd_135_R': {},
           'JCM_ForeArmFwd_75_L': {},
           'JCM_ForeArmFwd_75_R': {},
           'JCM_NeckBack_27': {},
           'JCM_NeckFwd_35': {},
           'JCM_ShinBend_155_L': {},
           'JCM_ShinBend_155_R': {},
           'JCM_ShinBend_90_L': {},
           'JCM_ShinBend_90_R': {},
           'JCM_ShldrDown_40_L': {},
           'JCM_ShldrDown_40_R': {},
           'JCM_ShldrFwd_110_L': {},
           'JCM_ShldrFwd_110_R': {},
           'JCM_ShldrUp_90_L': {},
           'JCM_ShldrUp_90_R': {},
           'JCM_ThighBack_35_L': {},
           'JCM_ThighBack_35_R': {},
           'JCM_ThighFwd_115_L': {},
           'JCM_ThighFwd_115_R': {},
           'JCM_ThighFwd_57_L': {},
           'JCM_ThighFwd_57_R': {},
           'JCM_ThighSide_85_L': {},
           'JCM_ThighSide_85_R': {}}

# createPoseReader()

JCMS = {'JCM_CollarUp_55_L': {'target': 'Scapula_L', 'rotation': (0, -55, 0), 'outerRadius': 55},
        'JCM_ForeArmFwd_135_L': {},
        'JCM_ForeArmFwd_75_L': {},
        'JCM_NeckBack_27': {},
        'JCM_NeckFwd_35': {},
        'JCM_ShinBend_155_L': {},
        'JCM_ShinBend_90_L': {},
        'JCM_ShldrDown_40_L': {},
        'JCM_ShldrFwd_110_L': {},
        'JCM_ShldrUp_90_L': {},
        'JCM_ThighBack_35_L': {},
        'JCM_ThighFwd_115_L': {},
        'JCM_ThighFwd_57_L': {},
        'JCM_ThighSide_85_L': {}}

bshape = pm.ls('MorphsBody')[0]

for morph, poseargs in JCMS.items():
    if poseargs:
        reader = createPoseReader(**poseargs)
        reader.attr('poseWeight').connect(bshape.weight.attr(morph))
        if morph.endswith('_L'):
            morphr = morph.replace('_L', '_R')
            poseargsr = poseargs.copy()
            poseargsr['target'] = poseargs['target'].replace('_L', '_R')
            reader = createPoseReader(**poseargsr)
            reader.attr('poseWeight').connect(bshape.weight.attr(morphr))
