"""
Solve a camera focal length to optimise rotateX, rotateY and focal length.
"""

import os
import time
import unittest

try:
    import maya.standalone
    maya.standalone.initialize()
except RuntimeError:
    pass
import maya.cmds


import test.test_solver.solverutils as solverUtils


# @unittest.skip
class TestSolver10(solverUtils.SolverTestCase):

    def test_init(self):
        cam_tfm = maya.cmds.createNode('transform', name='cam_tfm')
        cam_shp = maya.cmds.createNode('camera', name='cam_shp', parent=cam_tfm)
        maya.cmds.setAttr(cam_tfm + '.tx', 0.0)
        maya.cmds.setAttr(cam_tfm + '.ty', 1.0)
        maya.cmds.setAttr(cam_tfm + '.tz', -5.0)

        # Marker Group
        mkr_grp = maya.cmds.createNode('transform',
                                       name='markerGroup',
                                       parent=cam_tfm)
        mkr_scl = maya.cmds.createNode('mmMarkerScale')
        maya.cmds.connectAttr(cam_shp + '.focalLength', mkr_scl + '.focalLength')
        maya.cmds.connectAttr(cam_shp + '.cameraAperture', mkr_scl + '.cameraAperture')
        maya.cmds.connectAttr(cam_shp + '.filmOffset', mkr_scl + '.filmOffset')
        maya.cmds.connectAttr(mkr_scl + '.outScale', mkr_grp + '.scale')

        # Bundle 1
        bundle1_tfm = maya.cmds.createNode('transform', name='bundle1_tfm')
        bundle1_shp = maya.cmds.createNode('locator', name='bundle1_shp', parent=bundle1_tfm)
        maya.cmds.setAttr(bundle1_tfm + '.tx', -2.0)
        maya.cmds.setAttr(bundle1_tfm + '.ty', 6.4)
        maya.cmds.setAttr(bundle1_tfm + '.tz', -25.0)

        # Bundle 2
        bundle2_tfm = maya.cmds.createNode('transform', name='bundle2_tfm')
        bundle2_shp = maya.cmds.createNode('locator', name='bundle2_shp', parent=bundle2_tfm)
        maya.cmds.setAttr(bundle2_tfm + '.tx', 0.0)
        maya.cmds.setAttr(bundle2_tfm + '.ty', 6.4)
        maya.cmds.setAttr(bundle2_tfm + '.tz', -25.0)

        # Marker 1
        marker1_tfm = maya.cmds.createNode('transform', name='marker1_tfm', parent=mkr_grp)
        marker1_shp = maya.cmds.createNode('locator', name='marker1_shp', parent=marker1_tfm)
        maya.cmds.addAttr(marker1_tfm, longName='enable', at='byte',
                          minValue=0, maxValue=1, defaultValue=True)
        maya.cmds.addAttr(marker1_tfm, longName='weight', at='double',
                          minValue=0.0, defaultValue=1.0)
        maya.cmds.setAttr(marker1_tfm + '.tx', -2.0)
        maya.cmds.setAttr(marker1_tfm + '.ty', 1.3)
        maya.cmds.setAttr(marker1_tfm + '.tz', -10)

        # Marker 2
        marker2_tfm = maya.cmds.createNode('transform', name='marker2_tfm', parent=mkr_grp)
        marker2_shp = maya.cmds.createNode('locator', name='marker2_shp', parent=marker2_tfm)
        maya.cmds.addAttr(marker2_tfm, longName='enable', at='byte',
                          minValue=0, maxValue=1, defaultValue=True)
        maya.cmds.addAttr(marker2_tfm, longName='weight', at='double',
                          minValue=0.0, defaultValue=1.0)
        maya.cmds.setAttr(marker2_tfm + '.tx', 2.0)
        maya.cmds.setAttr(marker2_tfm + '.ty', 1.3)
        maya.cmds.setAttr(marker2_tfm + '.tz', -10)

        # save the output
        path = self.get_data_path('solver_test10_before.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        cameras = (
            (cam_tfm, cam_shp),
        )
        markers = (
            (marker1_tfm, cam_shp, bundle1_tfm),
            (marker2_tfm, cam_shp, bundle2_tfm),
        )
        node_attrs = [
            (cam_tfm + '.rx', 'None', 'None'),
            (cam_tfm + '.ry', 'None', 'None'),
            # (cam_tfm + '.rz', 'None', 'None'),
            (cam_shp + '.focalLength', 'None', 'None'),
        ]
        frames = [
            (1),
        ]

        # Run solver!
        s = time.time()
        result = maya.cmds.mmSolver(
            camera=cameras,
            marker=markers,
            attr=node_attrs,
            iterations=1000,
            frame=frames,
            verbose=True,
        )
        e = time.time()
        print 'total time:', e - s

        # save the output
        path = self.get_data_path('solver_test10_after.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)
        
        # Ensure the values are correct
        self.assertEqual(result[0], 'success=1')


if __name__ == '__main__':
    prog = unittest.main()
