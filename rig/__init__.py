import pymel.core as pm
from .utils import connectAttrMulti, createControlCurve, createNodeChain, createOffset, setColor, remapAttr
from .builders import getBuilder
from .components import buildFinger, buildFkChain, buildFkIkClavicle, buildFkIkLimb, buildFkIkSpine, buildFoot

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

COMP_SPECS = {
    'Spine_M': {'joints': ('Root_M', 'Spine1_M', 'Spine2_M', 'Spine3_M', 'Chest_M'), 'builder': buildFkIkSpine},
    'Clavicle': {'joints': ('Scapula', 'Shoulder'), 'builder': buildFkIkClavicle, 'parent': 'Chest_M'},
    'Arm': {'joints': ('Shoulder', 'Elbow', 'Wrist'), 'builder': buildFkIkLimb, 'parent': 'Scapula'},
    'Leg': {'joints': ('Hip', 'Knee', 'Ankle'), 'builder': buildFkIkLimb, 'parent': 'Pelvis_M'},
    'Neck_M': {'joints': ('Neck_M',), 'builder': buildFkChain, 'parent': 'Chest_M'},
    'Head_M': {'joints': ('Head_M',), 'builder': buildFkChain, 'parent': 'Neck_M'},
}

COMP_SPECS.update({finger: {'joints': tuple('{0}Finger{1}'.format(finger, i+1)
                                            for i in range(3)), 'builder': buildFinger, 'parent': 'Wrist'}
                   for finger in ('Thumb', 'Index', 'Middle', 'Ring', 'Pinky')})


def buildArm(arm, fingers):
    # Fingers should be in order, starting with Thumb
    ctrl = arm['units'][1]['controls'][0]
    for finger in fingers:
        # Add curl controls to hand IK
        root = finger['root']
        name = finger['name'].split('_')[0].replace('Finger', '')
        pm.addAttr(ctrl, ln=name+'Curl', at='float', minValue=0.0,
                   maxValue=10.0, defaultValue=0.0, k=True)
        rv = remapAttr(ctrl.attr(name+'Curl'), in_range=(0.0, 10.0))
        pm.connectAttr(rv, root.attr('curl'))
        # Set spread multipliers (exclude Thumb)
        if fingers.index(finger):
            finger['root'].spreadAmt.set(finger['root'].spreadAmt.get() *
                                         (-(fingers.index(finger) - 2.5)/1.5))

    # Add spread control
    pm.addAttr(ctrl, ln='spread', at='float', minValue=-5.0,
               maxValue=10.0, defaultValue=0.0, k=True)
    rv = remapAttr(ctrl.attr('spread'), in_range=(-5.0, 10.0),
                   out_range=(-0.5, 1.0))
    connectAttrMulti(rv, [finger['root'].spread for finger in fingers[1:]])


def build():

    components = dict()
    # components['Spine'] = buildFkIkSpine(
    #     ('Root_M', 'Spine1_M', 'Spine2_M', 'Spine3_M', 'Chest_M'))

    for side in '_L', '_R':
        # Build components
        for c, spec in COMP_SPECS.items():
            cside = side
            if c.endswith('_M'):
                cside = ''
                if c in components:
                    continue

            cname = c + cside

            buildfn = spec['builder']
            xforms = [jn+cside for jn in spec['joints']]
            print('Building {2}({0}) with joints {1}'.format(
                buildfn.__name__, xforms, cname))

            components[cname] = buildfn(xforms, cname)

            # Set parents
            if spec.get('parent', None):
                parname = spec['parent'] if spec['parent'].endswith(
                    '_M') else spec['parent'] + cside
                pm.parentConstraint(
                    parname, components[cname]['root'], mo=True)

    # Create main and COM controls
    main = createControlCurve(name='Main', size=40.0, color=(.15, 1, 1))
    pm.rotate(main, (0, 0, 90))
    pm.makeIdentity(main, apply=True)
    com = createControlCurve(name='CTRL_COM_M', shape='com',
                             size=60.0)
    com.setMatrix(components['Spine_M']['root'].getMatrix(ws=True), ws=True)
    createOffset(com)
    com.getParent().setParent(main)

    # Add controls to ControlSet
    pm.select(None)
    ctrlset = pm.sets(name='ControlSet')

    # Parent under main control
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
