from .attribute import addWeightAttrs, connectAttrMulti, createVisibilitySwitch, remapAttr, lockRotate, lockScale, lockTranslate
from .node import constrainTargets, createConnectorCurve, createControlCurve, createNodeChain, createOffset, freezeOffset, isTransform, setColor, synthConstraint
from .transform import getPoleVector, orientXform, orientChain

# Space switching
# Read current worldMatrix of control
# Convert relative to space
