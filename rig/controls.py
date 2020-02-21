from abc import ABCMeta, abstractmethod, abstractproperty
from functools import partial
import pymel.core as pm
from rig.utils import CONTROL_COLORS, createControlCurve, createNodeChain
from etc import CONTROL_TYPE, ControlShapes


class AbstractControlGrp(object):
    __metaclass__ = ABCMeta

    def __init__(self, name, joints):
        self._name = name
        self._joints = joints

        self._root_obj = None
        self._group_node = None
        self._control_objs = list()
        self._driver_objs = {joint: None for joint in self.joints}

    @property
    def control_objs(self):
        return self._control_objs

    @property
    def driver_objs(self):
        return self._driver_objs

    @property
    def group_node(self):
        return self._group_node

    @property
    def joints(self):
        return self._joints

    @property
    def name(self):
        return self._name

    @property
    def root_obj(self):
        return self._root_obj

    @abstractmethod
    def build(self):
        pass

    def buildAttrs(self):
        for attr_name in ['Drivers', 'Controls']:
            self.group_node.addAttr(attr_name, at='message')

        for node in (self.control_objs + self.driver_objs.values()):
            node.addAttr('CtrlGrp', at='message')

        for node in self.control_objs:
            self.group_node.Controls.connect(node.CtrlGrp, force=True)

        for node in self.driver_objs.values():
            self.group_node.Drivers.connect(node.CtrlGrp, force=True)


class ControlGrpFK(AbstractControlGrp):

    def __init__(self, name, joints):

        super(ControlGrpFK, self).__init__(name=name, joints=joints)

    def build(self):

        for i, joint in enumerate(self.joints):
            self.buildSingle(joint)

            if i == 0:
                ctrl_offset0 = self.control_objs[0].getParent()
                self._group_node = pm.createNode(
                    'transform', n="FKGroup{0}".format(self.name))
                pm.delete(pm.parentConstraint(ctrl_offset0, self.group_node))
                ctrl_offset0.setParent(self.group_node)
                self._root_obj = ctrl_offset0

            else:
                self.control_objs[i].getParent().setParent(
                    self.control_objs[i-1])

        self.buildAttrs()

    def buildSingle(self, joint):

        ctrl_offset = pm.createNode(
            'transform', n='FKOffset{0}'.format(joint.name))

        pm.delete(pm.parentConstraint(joint.mayaNode, ctrl_offset))

        ctrl_node = createControlCurve('FK{0}'.format(
            joint.name), size=5.0, color=[1, 0, 0])

        ctrl_node.setParent(ctrl_offset)
        pm.makeIdentity(ctrl_node)

        self._control_objs.append(ctrl_node)
        self._driver_objs[joint] = ctrl_node


class ControlGrpIK(AbstractControlGrp):

    def __init__(self, name, joints):

        if len(joints) < 2:
            raise ValueError("IKControl requires at least 2 joints")

        super(ControlGrpIK, self).__init__(name=name, joints=joints)

    def build(self):

        self._group_node = pm.createNode(
            'transform', n='IKGroup{0}'.format(self.name))
        pm.addAttr(self.group_node, ln='ctrlWeight', at='float',
                   minValue=0.0, maxValue=1.0, keyable=True)

        pm.delete(pm.parentConstraint(self.joints[0], self.group_node))

        driver_list = createNodeChain(self.joints, node_func=partial(
            pm.createNode, 'joint'), prefix='IK_')
        
        self._driver_objs = dict(zip(self.joints, driver_list))
        self._root_obj = driver_list[0]

        ik_end_joint = self.driver_objs[self.joints[-1]]

        ctrl_offset = pm.createNode(
            'transform', n="IKOffset{0}".format(self.name))
        ctrl_offset.setParent(ik_end_joint)
        pm.makeIdentity(ctrl_offset)
        ctrl_offset.setParent(None)

        ctrl = createControlCurve('IK{0}'.format(
            self.name), ctrl_type='ik', size=5.0, color=[1, 0, 0])
        ctrl.setParent(ctrl_offset)
        pm.makeIdentity(ctrl)
        self._control_objs.append(ctrl)

        [ik_handle, _] = pm.ikHandle(n="IKHandle_{0}".format(self.name),
                                     ee=self._driver_objs[self.joints[-1]], sj=self._driver_objs[self.joints[0]])

        pm.parentConstraint(ctrl, ik_handle, mo=True)

        self.driver_objs[self.joints[0]].setParent(self.group_node)
        ctrl_offset.setParent(self.group_node)
        ik_handle.setParent(self.group_node)

        self.buildAttrs()


class ControlGrpTwoBoneIK(ControlGrpIK):

    def __init__(self, name, joints):

        if len(joints) != 3:
            raise ValueError("Two-bone IK requires exactly 3 joints")

        super(ControlGrpTwoBoneIK, self).__init__(name, joints)

    def build(self):

        super(ControlGrpTwoBoneIK, self).build()

        pole_ctrl = createControlCurve('IK{0}'.format(
            self.name), ctrl_type='pole', size=5.0, color=[1, 0, 0])

        base_vec = self.joints[2].getTranslation(
            ws=True) - self.joints[0].getTranslation(ws=True)
        mid_vec = self.joints[1].getTranslation(
            ws=True) - self.joints[0].getTranslation(ws=True)


class RigModuleLimb(object):

    def __init__(self, name, joints, parent=None):
        self._name = name
        self._joints = joints
        self._parent = parent

        self._controls = {
            'fk': ControlGrpFK(name=self._name, joints=self._joints),
            'ik': ControlGrpIK(name=self._name, joints=self._joints)
        }

        self._constraints = list()

    @property
    def controls(self):
        return self._controls

    def build(self):

        for control in self._controls.values():
            control.build()

            if self._parent:
                pm.parentConstraint(self._parent, control.root_obj, mo=True)

            for joint in control.driver_objs:
                constraint = pm.orientConstraint(
                    control.driver_objs[joint], joint, mo=True)

                if constraint not in self._constraints:
                    self._constraints.append(constraint)

    def getWeightAttrList(self, control):
        wt_list = list()

        for driver in control.driver_objs.values():
            pass
