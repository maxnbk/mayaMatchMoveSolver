"""
Semi-Complex hierarchy and object-space utilising solve.
"""

try:
    import maya.standalone
    maya.standalone.initialize()
except RuntimeError:
    pass
import maya.cmds
import math
import time

def approxEqual(x, y, eps=0.0001):
    return x == y or (x < (y+eps) and x > (y-eps))

maya.cmds.file(new=True, force=True)
maya.cmds.unloadPlugin('mmSolver')
maya.cmds.loadPlugin('mmSolver')

cam_tfm = maya.cmds.createNode('transform', name='cam_tfm')
cam_shp = maya.cmds.createNode('camera', name='cam_shp', parent=cam_tfm)
maya.cmds.setAttr(cam_tfm + '.tx', -1.0)
maya.cmds.setAttr(cam_tfm + '.ty',  1.0)
maya.cmds.setAttr(cam_tfm + '.tz', -5.0)

group_tfm = maya.cmds.createNode('transform', name='group_tfm')
bundle1_tfm = maya.cmds.createNode('transform', name='bundle1_tfm', parent=group_tfm)
bundle1_shp = maya.cmds.createNode('locator', name='bundle1_shp', parent=bundle1_tfm)
bundle2_tfm = maya.cmds.createNode('transform', name='bundle2_tfm', parent=group_tfm)
bundle2_shp = maya.cmds.createNode('locator', name='bundle2_shp', parent=bundle2_tfm)
maya.cmds.setAttr(bundle1_tfm + '.tx', 10.0)
maya.cmds.setAttr(bundle2_tfm + '.tx', -10.0)
maya.cmds.setAttr(group_tfm + '.ry', 45.0)
maya.cmds.setAttr(group_tfm + '.tz', -35.0)

marker1_tfm = maya.cmds.createNode('transform', name='marker1_tfm', parent=cam_tfm)
marker1_shp = maya.cmds.createNode('locator', name='marker1_shp', parent=marker1_tfm)
maya.cmds.setAttr(marker1_tfm + '.tx', -2.5)
maya.cmds.setAttr(marker1_tfm + '.ty', 1.3)
maya.cmds.setAttr(marker1_tfm + '.tz', -10)

marker2_tfm = maya.cmds.createNode('transform', name='marker2_tfm', parent=cam_tfm)
marker2_shp = maya.cmds.createNode('locator', name='marker2_shp', parent=marker2_tfm)
maya.cmds.setAttr(marker2_tfm + '.tx', 2.5)
maya.cmds.setAttr(marker2_tfm + '.ty', -0.8)
maya.cmds.setAttr(marker2_tfm + '.tz', -6.0)

cameras = (
    (cam_tfm, cam_shp),
)
markers = (
    (marker1_tfm, cam_shp, bundle1_tfm),
    (marker2_tfm, cam_shp, bundle2_tfm),
)
node_attrs = [
    (group_tfm + '.tx', 0),
    (group_tfm + '.ty', 0),
    (group_tfm + '.tz', 0),
    (group_tfm + '.sx', 0),
    (group_tfm + '.ry', 0),
    (group_tfm + '.rz', 0),
]
frames = [
    (1),
]

# Run solver!
s = time.time()
err = maya.cmds.mmSolver(
    camera=cameras,
    marker=markers,
    attr=node_attrs,
    iterations=1000,
    solverType=0,
    frame=frames,
    verbose=True,
)
e = time.time()
print 'total time:', e - s

# Ensure the values are correct
assert approxEqual(err, 0.0, eps=0.001)
assert approxEqual(maya.cmds.getAttr(group_tfm+'.tx'), 1.47797)
assert approxEqual(maya.cmds.getAttr(group_tfm+'.ty'), 0.894038)
assert approxEqual(maya.cmds.getAttr(group_tfm+'.tz'), -32.9307)
assert approxEqual(maya.cmds.getAttr(group_tfm+'.sx'), 1.00556)
assert approxEqual(maya.cmds.getAttr(group_tfm+'.ry'), math.degrees(3.18648))
assert approxEqual(maya.cmds.getAttr(group_tfm+'.rz'), math.degrees(-0.374883))

if maya.cmds.about(batch=True):
    maya.cmds.quit(force=True)
else:
    maya.cmds.lookThru(cam_tfm)
