from functools import partial
import pymel.core as pm
from .builders import builder, getBuilder
from .utils import addWeightAttrs, connectAttrMulti, constrainTargets, createOffset, createVisibilitySwitch, remapAttr, createControlCurve

AS5_MAP = {'Ankle_L': 'Ankle_L',
           'Ankle_R': 'Ankle_R',
           'Clavicle_L': 'Scapula_L',
           'Clavicle_R': 'Scapula_R',
           'Elbow_L': 'Elbow_L',
           'Elbow_R': 'Elbow_R',
           'Eye_L': 'Eye_L',
           'Eye_R': 'Eye_R',
           'Head_M': 'Head_M',
           'Hip_L': 'Hip_L',
           'Hip_R': 'Hip_R',
           'Index1_L': 'IndexFinger1_L',
           'Index1_R': 'IndexFinger1_R',
           'Index2_L': 'IndexFinger2_L',
           'Index2_R': 'IndexFinger2_R',
           'Index3_L': 'IndexFinger3_L',
           'Index3_R': 'IndexFinger3_R',
           'Knee_L': 'Knee_L',
           'Knee_R': 'Knee_R',
           'Middle1_L': 'MiddleFinger1_L',
           'Middle1_R': 'MiddleFinger1_R',
           'Middle2_L': 'MiddleFinger2_L',
           'Middle2_R': 'MiddleFinger2_R',
           'Middle3_L': 'MiddleFinger3_L',
           'Middle3_R': 'MiddleFinger3_R',
           'Neck_M': 'Neck_M',
           'Pelvis_M': 'Pelvis_M',
           'Pinky1_L': 'PinkyFinger1_L',
           'Pinky1_R': 'PinkyFinger1_R',
           'Pinky2_L': 'PinkyFinger2_L',
           'Pinky2_R': 'PinkyFinger2_R',
           'Pinky3_L': 'PinkyFinger3_L',
           'Pinky3_R': 'PinkyFinger3_R',
           'Ring1_L': 'RingFinger1_L',
           'Ring1_R': 'RingFinger1_R',
           'Ring2_L': 'RingFinger2_L',
           'Ring2_R': 'RingFinger2_R',
           'Ring3_L': 'RingFinger3_L',
           'Ring3_R': 'RingFinger3_R',
           'Root_M': 'Root_M',
           'Shoulder_L': 'Shoulder_L',
           'Shoulder_R': 'Shoulder_R',
           'Spine1_M': 'Spine1_M',
           'Spine2_M': 'Spine2_M',
           'Spine3_M': 'Spine3_M',
           'Spine4_M': 'Chest_M',
           'Thumb1_L': 'ThumbFinger1_L',
           'Thumb1_R': 'ThumbFinger1_R',
           'Thumb2_L': 'ThumbFinger2_L',
           'Thumb2_R': 'ThumbFinger2_R',
           'Thumb3_L': 'ThumbFinger3_L',
           'Thumb3_R': 'ThumbFinger3_R',
           'ToesEnd_L': 'ToesEnd_L',
           'ToesEnd_R': 'ToesEnd_R',
           'Toes_L': 'Toes_L',
           'Toes_R': 'Toes_R',
           'Wrist_L': 'Wrist_L',
           'Wrist_R': 'Wrist_R'}


def isValidUnit(unit):
    return isinstance(unit, dict) and all(k in unit
                                          for k in ('name',
                                                    'unit_type',
                                                    'root',
                                                    'controls',
                                                    'drivers',
                                                    'targets'))


def attachUnits(unit1, unit2=None):
    print('Attaching units...')
    targets = unit1['targets']
    drivers = unit1['drivers']

    if unit2:
        targets = tuple(jnt for i, jnt in enumerate(
            targets) if unit2['targets'][i] == jnt)
        drivers = tuple(zip(unit1['drivers'], unit2['drivers']))

    return constrainTargets(drivers, targets)


def addWeightSwitch(attr_host, unit1, unit2, attr_name='IkWeight', defaultValue=0.0):
    print('Adding weight switch...')
    constraints = attachUnits(unit1, unit2)
    print(constraints)
    return addWeightAttrs(attr_host, attr_name, constraints, defaultValue)


def _build2Unit(unit1, unit2, name=None):
    name = name or unit1['targets'][0].nodeName()
    root = createOffset(unit1['root'], name='{}_ROOT'.format(name))
    unit2['root'].setParent(root)
    print('Building switch attrs...')
    switchattrs = addWeightSwitch(root, unit1, unit2, defaultValue=1.0)

    print('Creating visibility switch...')
    for switchattr, unit in zip(switchattrs, (unit2, unit1)):
        createVisibilitySwitch(switchattr, unit['controls'])

    return {'name': name,
            'root': root,
            'units': (unit1, unit2),
            'targets': tuple(t for t in unit1['targets'] if t in unit2['targets'])}


componentbuilder = partial(builder, output_keys=(
    'name', 'root', 'units'))


@componentbuilder(min_xforms=2, max_xforms=2)
def buildFkIkClavicle(xforms, name=None):
    name = name or xforms[0].nodeName()
    fkunit = getBuilder('fkchain')(xforms[0], name)
    ikunit = getBuilder('ikchain')(xforms, name,
                                   ctrl_orient=xforms[0].getRotation(
                                       space='world'),
                                   size=8.0)

    return _build2Unit(fkunit, ikunit, name='FkIk' + name)


@componentbuilder(min_xforms=3, max_xforms=3)
def buildFkIkLimb(xforms, name=None):
    print('Building FkIkLimb component:')
    name = name or xforms[0].nodeName()
    fkunit = getBuilder('fkchain')(xforms, name, size=8.0)
    ikunit = getBuilder('ik2bone')(xforms, name, size=6.0)

    return _build2Unit(fkunit, ikunit, name='FkIk' + name)


@componentbuilder(min_xforms=3)
def buildFkIkSpline(xforms, name=None):
    name = name or xforms[0].nodeName()
    fkunit = getBuilder('fkchain')(xforms, name)
    ikunit = getBuilder('ikspline')(xforms, name)

    return _build2Unit(fkunit, ikunit, name='FkIk' + name)


def buildFkIkSpine(xforms, name='Spine_M'):
    comp = buildFkIkSpline(xforms, name)
    pm.pointConstraint(comp['units'][1]['controls'][0],
                       comp['units'][1]['targets'][0], mo=True)
    return comp


@componentbuilder(min_xforms=2)
def buildFinger(xforms, name=None):
    name = name or xforms[0].nodeName().replace('1', '')
    fkunit = getBuilder('fkchain')(xforms, name, size=1.5)

    root = fkunit['root']
    pm.rename(root, root.name().replace('GRP', 'ROOT'))

    # Create curl
    pm.addAttr(root, ln='Curl', at='float', minValue=-0.5,
               maxValue=1.0, defaultValue=0.0, k=True)

    drvattr = remapAttr(root.attr('Curl'), in_range=(-0.5,
                                                     1.0), out_range=(-45.0, 90.0))

    connectAttrMulti(drvattr, [xf.ry for xf in fkunit['drivers']])

    attachUnits(fkunit)

    return {'name': name,
            'root': root,
            'units': [fkunit]}


PARENTS = {
    'Clavicle': 'Chest_M',
    'Arm': 'Scapula',
    'Thumb': 'Wrist',
    'Index': 'Wrist',
    'Middle': 'Wrist',
    'Ring': 'Wrist',
    'Pinky': 'Wrist',
    'Leg': 'Pelvis_M',
    'Foot': 'Ankle'
}

JOINTS = {
    'Clavicle': ('Scapula', 'Shoulder'),
    'Arm': ('Shoulder', 'Elbow', 'Wrist'),
    'Leg': ('Hip', 'Knee', 'Ankle'),
    'Thumb': tuple('ThumbFinger{}'.format(i+1) for i in range(3)),
    'Index': tuple('IndexFinger{}'.format(i+1) for i in range(3)),
    'Middle': tuple('MiddleFinger{}'.format(i+1) for i in range(3)),
    'Ring': tuple('RingFinger{}'.format(i+1) for i in range(3)),
    'Pinky': tuple('PinkyFinger{}'.format(i+1) for i in range(3))
}

BUILDERS = {
    'Clavicle': buildFkIkClavicle,
    'Arm': buildFkIkLimb,
    'Leg': buildFkIkLimb,
    'Thumb': buildFinger,
    'Index': buildFinger,
    'Middle': buildFinger,
    'Ring': buildFinger,
    'Pinky': buildFinger
}


def buildAll():

    components = dict()
    components['Spine'] = buildFkIkSpine(
        ('Root_M', 'Spine1_M', 'Spine2_M', 'Spine3_M', 'Chest_M'))
    main = createControlCurve(name='Main', size=40.0, color=(.15, 1, 1))
    pm.rotate(main, (0, 0, 90))
    pm.makeIdentity(main, apply=True)
    com = createControlCurve(name='CTRL_COM_M', shape='com',
                             size=60.0)
    com.setMatrix(components['Spine']['root'].getMatrix(ws=True), ws=True)
    createOffset(com)
    com.getParent().setParent(main)

    for side in '_L', '_R':
        for joint in JOINTS:
            jname = joint+side
            comp = BUILDERS[joint]([jn+side for jn in JOINTS[joint]], jname)
            components[jname] = comp

            parjoint = PARENTS[joint] if PARENTS[joint].endswith(
                '_M') else PARENTS[joint] + side
            pm.parentConstraint(parjoint, comp['root'], mo=True)

    pm.select(None)
    ctrlset = pm.sets(name='ControlSet')

    for component in components.values():
        component['root'].setParent(com)
        for unit in component['units']:
            print(unit['controls'])
            ctrlset.addMembers(unit['controls'])


# Connect driver/weight attributes
# Add eye controls
# Add head, neck, jaw controls
# Global head/neck control
# Space switching
# Parent-space transforms?
# Pose drivers
