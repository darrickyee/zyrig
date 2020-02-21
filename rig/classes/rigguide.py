from abc import ABCMeta, abstractproperty

import pymel.core as pm
import pymel.core.nodetypes as nodetypes
from mgear.core.curve import addCnsCurve

from ..utils import createControlCurve


class AbstractRigGuide(object):
    __metaclass__ = ABCMeta

    def __init__(self, name, root_node=None):
        self.name = name
        self._nodes = list()

        if isinstance(root_node, nodetypes.Transform):
            self.loadNodeData(root_node)

    @abstractproperty
    def guide_type(self):
        pass

    @abstractproperty
    def params(self):
        pass

    @abstractproperty
    def node_names(self):
        # Return a list of node names corresponding to the transform
        # objects to be placed in the scene for this guide.  First item
        # should always be the root node name.
        pass

    @abstractproperty
    def node_tree(self):
        # Return a dictionary of int:int mappings representing the
        # parent-child relationships of the guide's transforms.  Ints
        # correspond to indices in `self.node_names`.
        pass

    @property
    def nodes(self):
        return self._nodes

    @property
    def node_transforms(self):
        if self._nodes:
            return [node.getMatrix(worldSpace=True) for node in self.nodes]

        return []

    @property
    def root(self):
        return self.nodes[0] if self.nodes else None

    def loadNodeData(self, node):
        # Load properties from existing Maya transform node
        self._nodes.append(node)

    def draw(self, parent=None):
        self._nodes = [createControlCurve(name) for name in self.node_names]

        for i, node in enumerate(self.nodes):
            parent_index = self.node_tree.get(i, None)
            parent_node = self.nodes[parent_index] if parent_index is not None else None
            node.setParent(parent_node)

        # Add base attributes
        pm.addAttr(self.root, longName='rigClass', dt='string')
        self.root.rigClass.set('RigGuide', lock=True)
        pm.addAttr(self.root, longName='guideNodes', at='message', multi=True)

        # Add attributes connecting root to remaining transforms
        if len(self.nodes) > 1:
            for i, node in enumerate(self.nodes[1:]):
                pm.addAttr(node, longName='guideRoot', at='message')
                self.root.guideNodes[i].connect(node.guideRoot, force=True)

        self.addConnectorCurves()

        # Add parameters

        # Set root parent
        self.root.setParent(parent)
        self.root.setTranslation((0, 0, 0))

    def getBranch(self, leaf_node):
        branch = [leaf_node]

        while leaf_node.getParent() in self.nodes:
            leaf_node = leaf_node.getParent()
            branch.append(leaf_node)

        return branch

    def addConnectorCurves(self):

        leaf_nodes = [
            node for node in self.nodes if not node.listRelatives(type='transform')]
        branches = [self.getBranch(leaf) for leaf in leaf_nodes]

        for branch in branches:
            crv = addCnsCurve(self.root, self.name+'CnsCrv1', branch)
            pm.makeIdentity(crv)
            pm.toggle(crv, template=True)


class ControlGuide(AbstractRigGuide):

    @property
    def guide_type(self):
        return 'control'

    @property
    def params(self):
        return []

    @property
    def node_names(self):
        return ['Control1', 'Control2', 'Control3', 'Control4']

    @property
    def node_tree(self):
        return {0: None, 1: 0, 2: 1, 3: 0}
