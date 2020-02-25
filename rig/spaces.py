import pymel.core as pm

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