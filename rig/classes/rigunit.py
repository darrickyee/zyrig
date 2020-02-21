from ..utils import isTransform


class RigUnit(object):
    """Temporary object containing references to nodes used to assemble a RigModule.
    """

    def __init__(self, unit_type, name=None, **kwargs):

        self.unit_type = unit_type
        self.name = name or ''
        self._controls = list()
        self._drivers = list()
        self._root = None
        self._aux_nodes = dict()

        # Assign objects if passed in constructor
        for key in kwargs:
            setattr(self, key, kwargs[key])

    @property
    def controls(self):
        return self._controls

    @controls.setter
    def controls(self, ctrl_list):

        if not isinstance(ctrl_list, list):
            raise TypeError(
                'RigUnit "controls" property must be a list of Transform objects.')

        if all(isTransform(ctrl) for ctrl in ctrl_list):
            self._controls = ctrl_list

    def addControl(self, ctrl):
        if isTransform(ctrl, raise_error=True):
            self._controls.append(ctrl)

    @property
    def drivers(self):
        return self._drivers

    @drivers.setter
    def drivers(self, drv_list):

        if not isinstance(drv_list, list):
            raise TypeError(
                'RigUnit "drivers" property must be a list of Transform objects.')

        if all(isTransform(drv) for drv in drv_list):
            self._drivers = drv_list

    def addDriver(self, drv):
        if isTransform(drv, raise_error=True):
            self._drivers.append(drv)

    @property
    def root(self):
        return self._root

    @root.setter
    def root(self, node):
        if isTransform(node, raise_error=True):
            self._root = node

    @property
    def aux_nodes(self):
        return self._aux_nodes

    @aux_nodes.setter
    def aux_nodes(self, aux_dict):
        if not isinstance(aux_dict, dict):
            raise TypeError(
                '{}: Attempted to set "aux_nodes" property to non-dict.')

        self._aux_nodes = aux_dict

    def addAuxNode(self, name, node):
        self._aux_nodes[name] = node
