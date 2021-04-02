from abc import ABCMeta, abstractmethod, abstractproperty
# from .utils.transform import getPoleVector
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

    return pole_vec.normal()


class Guide(object):
    __metaclass__ = ABCMeta

    def __init__(self, transforms=None, name='Default', side='middle', settings=None):
        self.transforms = transforms or []
        self.name = name
        self.side = side
        self.settings = settings or {}

    @abstractproperty
    def upvec(self):
        pass


class Component(object):
    __metaclass__ = ABCMeta

    def __init__(self, guide, settings=None):
        if not isinstance(guide):
            raise TypeError('Invalid guide component')
        self.guide = guide
        self.settings = settings or {}

    @abstractmethod
    def build(self):
        pass


class IkGuide(Guide):

    def __init__(self, transforms=None, name='Default', side='middle', settings=None):
        super.__init__(transforms, name, side, settings)
        self.settings = {'control_types'}

    @property
    def upvec(self):
        return getPoleVector(*self.transforms[:3])
