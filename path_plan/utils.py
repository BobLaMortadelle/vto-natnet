import numpy as np
import pybullet as p

def add_buildings(physicsClientId, version=2):

    if version == 1 :

        scaling_factor=1.5
        buildings = [ (2.5, 2.5), (2.5, -.5), (1.5,-1.5), (-2.5,-2.5) ] #(-2.5,-2.5)

        for x,y in buildings:
            p.loadURDF("./buildings/building_square.urdf", #"cube_small.urdf",
                       [x, y, 1.85],
                       p.getQuaternionFromEuler([0, 0, 0]),
                       globalScaling=scaling_factor,
                       physicsClientId=physicsClientId
                       )

        scaling_factor=1.8
        buildings = [(-1, 1), (-3,3)]

        for x,y in buildings:
            p.loadURDF("./buildings/building_cylinder.urdf", #"cube_small.urdf",
                       [x, y, 1.85],
                       p.getQuaternionFromEuler([0, 0, 0]),
                       globalScaling=scaling_factor,
                       physicsClientId=physicsClientId
                       )
    if version == 2 :
        scaling_factor = 0.8
        # Square Buildings
        # buildings = [ (-1.5, -0.2), (-1.5, -2.0), (-3.0, -1.0), (-3.0, 1.0) ]
        buildings = [ (-1.5, -0.2), (-3.0, -1.0), (-3.0, 1.0) ]
        for x,y in buildings:
            p.loadURDF("./buildings/building_square.urdf",
                       [x, y, 1.05],
                       p.getQuaternionFromEuler([0, 0, 0.7]),
                       globalScaling=scaling_factor,
                       physicsClientId=physicsClientId
                       )
        # Hexagonal Buildings
        p.loadURDF("./buildings/building_hexa_50_200.urdf",
                       [-0.20, 1.0, 0.05],
                       p.getQuaternionFromEuler([0, 0, 0]),
                       globalScaling=scaling_factor,
                       physicsClientId=physicsClientId
                       )
        p.loadURDF("./buildings/building_hexa_50_150.urdf",
                       [-0.20, 3.0, 0.05],
                       p.getQuaternionFromEuler([0, 0, 0]),
                       globalScaling=scaling_factor,
                       physicsClientId=physicsClientId
                       )
        p.loadURDF("./buildings/building_hexa_50_120.urdf",
                       [1.20, 2.0, 0.05],
                       p.getQuaternionFromEuler([0, 0, 0]),
                       globalScaling=scaling_factor,
                       physicsClientId=physicsClientId
                       )
        # Right and Left Strange Buildings
        p.loadURDF("./buildings/building_right_120.urdf",
                       [2.25, -1.6, 0.0],
                       p.getQuaternionFromEuler([0, 0, 0]),
                       globalScaling=scaling_factor,
                       physicsClientId=physicsClientId
                       )
        p.loadURDF("./buildings/building_left_120.urdf",
                       [0.75, -1.6, 0.0],
                       p.getQuaternionFromEuler([0, 0, 0]),
                       globalScaling=scaling_factor,
                       physicsClientId=physicsClientId
                       )