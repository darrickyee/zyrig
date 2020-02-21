import sys
if 'maya.exe' in sys.executable:
    import pymel.util.enum as enummod

    def buildEnum(enum_name, enum_dict):
        return enummod.Enum(name=enum_name, keys=enum_dict)

else:
    import enum as enummod

    def buildEnum(enum_name, enum_dict):
        return type(enum_name, (enummod.Enum,), enum_dict)


ENUM_DEFS = {
    'CONTROL_TYPE': {
        'FK': 0,
        'IK': 1,
        'IKSpline': 2,
        'Pole': 3,
        'Aim': 4
    },
    'MODULE_TYPE': {
        'Root': 0,
        'Spine': 1,
        'Leg': 2,
        'Arm': 3,
        'Foot': 4,
        'Hand': 5,
        'Head': 6,
        'Finger': 7,
        'Joint': 8,
        'Chain': 9
    }
}

CONTROL_TYPE = buildEnum('CONTROL_TYPE', ENUM_DEFS['CONTROL_TYPE'])
MODULE_TYPE = buildEnum('MODULE_TYPE', ENUM_DEFS['MODULE_TYPE'])
