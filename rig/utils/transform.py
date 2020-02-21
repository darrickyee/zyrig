import pymel.core as pm


def getPoleVector(start, mid, end):
    """
    Returns a unit pole vector for `start`, `mid`, and `end` transforms.
    The pole vector is (parallel to) the vector orthogonal to the vector
    between `start` and `end` that passes through `mid`.
    (Note that `start` and `end` are interchangeable.)

    Parameters
    ----------
    start : pm.nodetypes.Transform

    mid : pm.nodetypes.Transform

    end : pm.nodetypes.Transform


    Returns
    -------
    pm.datatypes.Vector

    """

    start, mid, end = (pm.ls(x)[0] for x in (start, mid, end))

    locs = [xform.getTranslation(space='world') for xform in [start, mid, end]]
    vec_basen = (locs[2] - locs[0]).normal()
    vec_mid = (locs[1] - locs[0])
    pole_vec = (vec_mid - vec_mid.dot(vec_basen)*vec_basen)

    return pole_vec


def orientXform(xform, aim_loc, aim_axis=(1, 0, 0), up_axis=(0, 1, 0), world_up=(0, 1, 0), freeze=False):

    xform = pm.ls(xform)[0]

    children = xform.listRelatives()

    if children:
        for child in children:
            child.setParent(None)

    target = pm.createNode('transform')
    target.setTranslation(aim_loc, ws=True)

    pm.delete(pm.aimConstraint(target, xform, aimVector=aim_axis,
                               upVector=up_axis, worldUpVector=world_up))

    pm.delete(target)

    if freeze:
        pm.makeIdentity(xform, apply=True)

    if children:
        for child in children:
            child.setParent(xform)


def orientChain(xform_list, aim_axis=(1, 0, 0), up_axis=(0, 1, 0), world_up=None, freeze=False):

    xform_list = pm.ls(xform_list, type='transform')

    if world_up is None:
        world_up = (0, 1, 0) if len(
            xform_list) < 3 else getPoleVector(*xform_list[-3:])

    for i, xform in enumerate(xform_list):
        if xform != xform_list[-1]:
            orientXform(xform, xform_list[i+1].getTranslation(ws=True),
                        aim_axis=aim_axis, up_axis=up_axis, world_up=world_up, freeze=freeze)


def addSpace(target,
             control_obj,
             orient_only=False):
    """
    Adds a target space to the current control object.

    Parameters
    ----------
    target : pymel.nodetypes.Transform
        Target object for constraint
    control_obj : pymel.nodetypes.Transform
        Control object.  Target object will be added as constraint target for the parent "offset" transform for the control.
    orient_only : bool
        Use orient constraint? (the default is False, which uses a parent constraint)

    """

    if orient_only:
        constrain = pm.orientConstraint
        constraint_desc = 'orient'
    else:
        constrain = pm.parentConstraint
        constraint_desc = 'parent'

    # Add type checking?
    target_name = target.nodeName()
    control_offset = control_obj.getParent()

    constraint_obj = constrain(target, control_offset, mo=True)
    target_index = constraint_obj.getTargetList().index(target)
    constraint_wt_attr = constraint_obj.getWeightAliasList()[target_index]

    control_offset.addAttr("wt_{0}_{1}".format(
        constraint_desc, target_name), at=float, min=0.0, max=1.0, keyable=True)
    control_wt_attr = control_offset.attr(
        "wt_{0}_{1}".format(constraint_desc, target_name))

    pm.connectAttr(control_wt_attr, constraint_wt_attr)

    return(control_wt_attr)
