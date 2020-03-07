import pymel.core as pm
from .utils import connectAttrMulti, createControlCurve, createNodeChain, createOffset, setColor, remapAttr
from .builders import getBuilder
from .components import buildFinger, buildFkIkClavicle, buildFkIkLimb, buildFkIkSpine, buildFoot

PARENTS = {
    'Clavicle': 'Chest_M',
    'Arm': 'Scapula',
    'Thumb': 'Wrist',
    'Index': 'Wrist',
    'Middle': 'Wrist',
    'Ring': 'Wrist',
    'Pinky': 'Wrist',
    'Leg': 'Pelvis_M'
}

JOINTS = {
    'Clavicle': ('Scapula', 'Shoulder'),
    'Arm': ('Shoulder', 'Elbow', 'Wrist'),
    'Leg': ('Hip', 'Knee', 'Ankle'),
    # 'Foot': ('Ankle', 'Toes', 'ToesEnd', 'Heel'),
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
    # 'Foot': buildFoot,
    'Thumb': buildFinger,
    'Index': buildFinger,
    'Middle': buildFinger,
    'Ring': buildFinger,
    'Pinky': buildFinger
}


def buildArm(arm, fingers):
    ctrl = arm['units'][1]['controls'][0]
    for finger in fingers:
        root = finger['root']
        name = finger['name'].split('_')[0].replace('Finger', '')
        pm.addAttr(ctrl, ln=name+'Curl', at='float', minValue=0.0,
                   maxValue=10.0, defaultValue=0.0, k=True)
        rv = remapAttr(ctrl.attr(name+'Curl'), in_range=(0.0, 10.0))
        pm.connectAttr(rv, root.attr('curl'))


def build():

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

    return components

# Connect driver/weight attributes
# Add eye controls
# Add head, neck, jaw controls
# Global head/neck control
# Space switching
# Parent-space transforms?
# Pose drivers
