import pymel.core as pm
from .rig.utils import createNodeChain, createControlCurve
from .rig.utils import lockTranslate, lockRotate, lockScale

COLOR_LEFT = (0, 0, 1)
COLOR_RIGHT = (1, 0, 0)

def myfunc(name=None, myarg=4, **kwargs):
    print(f'name: {name}, myarg: {myarg}')
    print(kwargs)


def buildDrivingSystem(src_attr, dest_attrs, keys=None, rv_node_name=None):
    if keys:
        if not rv_node_name:
            raise ValueError("Please supply a name for the remapValue node.")

        rv_node = pm.createNode('remapValue', name=rv_node_name)

        in_min = min(key[0] for key in keys)
        in_max = max(key[0] for key in keys)
        out_min = min(key[1] for key in keys)
        out_max = max(key[1] for key in keys)

        rv_node.inputMin.set(in_min)
        rv_node.inputMax.set(in_max)
        rv_node.outputMin.set(out_min)
        rv_node.outputMax.set(out_max)

        in_range = in_max - in_min
        out_range = out_max - out_min

        for i, key in enumerate(keys):
            pos = (key[0] - in_min)/in_range
            val = (key[1] - out_min)/out_range

            rv_node.value[i].value_Position.set(pos)
            rv_node.value[i].value_FloatValue.set(val)
            rv_node.value[i].value_Interp.set(1)

        src_attr.connect(rv_node.inputValue)
        src_attr = rv_node.outValue

    for dest_attr in dest_attrs:
        src_attr.connect(dest_attr)


def buildWeightControls(rig_module, attr_prefixes=['Ik', 'Fk']):

    attr_names = ['{0}Weight'.format(prefix) for prefix in attr_prefixes]

    pm.addAttr(rig_module.node, ln=attr_names[0], at='float',
               minValue=0.0, maxValue=1.0, defaultValue=1.0)

    wt_attrs = [
        [weight for constraint in rig_module.constraints.values()
         for target, weight in zip(constraint.getTargetList(), constraint.getWeightAliasList())
         if target in rig_unit.targets]
        for rig_unit in rig_module.rig_units.values()]

    rev_node = pm.createNode('reverse', name="{0}_{1}_Rev".format(
        rig_module.name, attr_names[1]))
    rig_module.node.IkWeight.connect(rev_node.inputX)

    attr_dict = {0: rig_module.node.IkWeight, 1: rev_node.outputX}

    for i, wt_list in enumerate(wt_attrs):
        for wt_attr in wt_list:
            attr_dict[i].connect(wt_attr)

    # Add auto-visibility
    vis_nodes = [pm.createNode(
        'condition', name='{0}_{1}Weight_Vis'.format(rig_module.name, attr_name))
        for attr_name in attr_names]

    for i, rig_unit in enumerate(rig_module.rig_units.values()):
        attr_dict[i].connect(vis_nodes[i].firstTerm)
        for control in rig_unit.controls:
            vis_nodes[i].outColorR.connect(control.visibility)


class RigChar(object):

    def __init__(self, skeleton):
        self.skeleton = skeleton

        module_arm_r = RigModuleLimb('Arm_R',
                                     joints=[self.skeleton[joint] for joint in [
                                         'Shoulder_R', 'Elbow_R', 'Wrist_R']],
                                     ctrl_color=COLOR_RIGHT,
                                     ctrl_size=6.0,
                                     parent=self.skeleton['Clavicle_R'])

        module_arm_l = RigModuleLimb('Arm_L',
                                     joints=[self.skeleton[joint] for joint in [
                                         'Shoulder_L', 'Elbow_L', 'Wrist_L']],
                                     ctrl_color=COLOR_LEFT,
                                     ctrl_size=6.0,
                                     parent=self.skeleton['Clavicle_L'])

        module_leg_r = RigModuleLimb('Leg_R',
                                     joints=[self.skeleton[joint] for joint in [
                                         'Hip_R', 'Knee_R', 'Ankle_R']],
                                     ctrl_color=COLOR_RIGHT,
                                     ctrl_size=8.0,
                                     parent=self.skeleton['Pelvis_M'])

        module_leg_l = RigModuleLimb('Leg_L',
                                     joints=[self.skeleton[joint] for joint in [
                                         'Hip_L', 'Knee_L', 'Ankle_L']],
                                     ctrl_color=COLOR_LEFT,
                                     ctrl_size=8.0,
                                     parent=self.skeleton['Pelvis_M'])

        module_hand_r = RigModuleHand('Hand_R',
                                      joints=[self.skeleton[joint] for joint in [
                                          "Finger{0}{1}_R".format(finger, i+1)
                                          for finger in ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
                                          for i in range(3)]
                                      ],
                                      ctrl_color=COLOR_RIGHT,
                                      parent=self.skeleton['Wrist_R'])

        module_hand_l = RigModuleHand('Hand_L',
                                      joints=[self.skeleton[joint] for joint in [
                                          "Finger{0}{1}_L".format(finger, i+1)
                                          for finger in ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
                                          for i in range(3)]
                                      ],
                                      ctrl_color=COLOR_LEFT,
                                      parent=self.skeleton['Wrist_L'])

        self.modules = [module_arm_r, module_arm_l, module_hand_r,
                        module_hand_l, module_leg_r, module_leg_l]


#########################
# %%

def myfunc(name=None):
    print(name)
# %%


class MyThing(object):

    def __init__(self, name, **kwargs):
        self.name = name
        self.arg_dict = kwargs

        for key, val in kwargs.items():
            if isinstance(key, str):
                setattr(self, key, val)

    def __delitem__(self, key):
        del self.arg_dict[key]

    def __getitem__(self, key):
        if key == 'name':
            return self.name

        return self.arg_dict[key]

    def __setitem__(self, key, value):
        if key == 'name':
            self.name = value
        else:
            self.arg_dict[key] = value

    def __repr__(self):
        return str(self.arg_dict)

    def __iter__(self):
        return (key for key in ['name']+list(self.arg_dict))

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default


# %%
