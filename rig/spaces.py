import pymel.core as pm

def zeroMatrixRotation(matrix):
    idmat = pm.dt.Matrix()
    idmat[-1] = matrix[-1]
    return idmat
    
def zeroMatrixTranslation(matrix):
    m = pm.dt.Matrix(matrix)
    m[-1] = [0, 0, 0, 1]
    return m

def getRelativeTransform(xform, parent):
    return xform.worldMatrix.get()*parent.worldInverseMatrix.get()

tgt = pm.ls('pCube1')[0]


bl = pm.createNode('blendMatrix')
bl.inputMatrix.set(tgt.offsetParentMatrix.get())

for i, vpar in enumerate(pm.ls('par1', 'par2')):
    mm = pm.createNode('multMatrix')
    mm.matrixIn[0].set(getRelativeTransform(tgt, vpar))
    pm.connectAttr(vpar.worldMatrix[0], mm.matrixIn[1])
    if tgt.getParent():
        pm.connectAttr(tgt.getParent().worldInverseMatrix, mm.matrixIn[2])

    pm.connectAttr(mm.matrixSum, bl.target[i].targetMatrix)



ctrl = pm.ls('Ik_Arm_L')[0]
target = pm.ls('GLOBAL')[0]


## Parent space
space = pm.createNode('transform', name='{0}_{1}_REF'.format(ctrl.name(), target.name()))
space.setMatrix(ctrl.getMatrix(ws=True), ws=True)
pm.parentConstraint(target, space, mo=True)
baseOPM = ctrl.offsetParentMatrix.get()



## Global orient
space = pm.createNode('transform', name='spaceRef')
space.setMatrix(ctrl.getMatrix(ws=True), ws=True)
pm.connectAttr(target.worldMatrix[0], space.offsetParentMatrix)

bl = pm.createNode('blendMatrix', name='{}_SPACES_BLEND'.format(ctrl.name()))
mult = pm.createNode('multMatrix', name='{0}_{1}_OPM'.format(ctrl.name(), target.name()))
pk_tgt = pm.createNode('pickMatrix', name='{}_ROT'.format(target.name()))
pk_par = pm.createNode('pickMatrix', name='{}_INVROT'.format(ctrl.getParent().name()))

pm.connectAttr(space.worldMatrix[0], pk_tgt.inputMatrix)
pm.connectAttr(ctrl.getParent().worldInverseMatrix[0], pk_par.inputMatrix)

for pk in pk_par, pk_tgt:
    for c in 'useTranslate', 'useScale', 'useShear':
        pk.attr(c).set(0)

pm.connectAttr(pk_tgt.outputMatrix, mult.matrixIn[0])
pm.connectAttr(pk_par.outputMatrix, mult.matrixIn[1])
mult.matrixIn[2].set(zeroMatrixRotation(ctrl.offsetParentMatrix.get()))


pm.connectAttr(mult.matrixSum, bl.target[0].targetMatrix)
bl.inputMatrix.set(ctrl.offsetParentMatrix.get())
pm.connectAttr(bl.outputMatrix, ctrl.offsetParentMatrix)

# Add attribute