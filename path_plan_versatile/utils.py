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
        scaling_factor = 1.0
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

    if version == 6 :
        # [Building([[3.0, 2.0, 1.2], [2.75, 1.567, 1.2], [2.25, 1.567, 1.2], [2.0, 2.0, 1.2], [2.25, 2.433, 1.2], [2.75, 2.433, 1.2]]), #AddCircularBuilding( 2.5, 2, 6, 0.5, 1.2, angle = 0)
        # Building([[1.0, 3.0, 1.5], [0.75, 2.567, 1.5], [0.25, 2.567, 1.5], [0.0, 3.0, 1.5], [0.25, 3.433, 1.5], [0.75, 3.433, 1.5]]), #AddCircularBuilding( 0.5, 3, 6, 0.5, 1.5, angle = 0)
        # Building([[1.0, 0.5, 2], [0.75, 0.067, 2], [0.25, 0.067, 2], [0.0, 0.5, 2], [0.25, 0.933, 2], [0.75, 0.933, 2]]), #AddCircularBuilding( 0.5, 0.5, 6, 0.5, 2, angle = 0)  
        # Building([[-2.65, 1.5, 1.5], [-3.0, 1.15, 1.5], [-3.35, 1.5, 1.5], [-3.0, 1.85, 1.5]]), #AddCircularBuilding( -3, 1.5, 4, 0.35, 1.5, angle = 0)
        # Building([[-2.65, -1.5, 1.5], [-3.0, -1.85, 1.5], [-3.35, -1.5, 1.5], [-3.0, -1.15, 1.5]]), #AddCircularBuilding( -3, -1.5, 4, 0.35, 1.5, angle = 0) 
        # Building([[-1.15, -0.2, 1.5], [-1.5, -0.55, 1.5], [-1.85, -0.2, 1.5], [-1.5, 0.15, 1.5]]), #AddCircularBuilding( -1.5, -0.2, 4, 0.35, 1.5, angle = 0)
        # Building([[1.5, -2.5, 1.2], [1, -2.5, 1.2], [1, -1.4, 1.2], [1.5, -1, 1.2]]),
        # Building([[3.5, -2.5, 1.2], [3, -2.5, 1.2], [3, -1, 1.2], [3.5, -1.4, 1.2]])]
        # x_offset, y_offset, no_of_pts, size, height = 1, angle = 0
        scaling_factor = 1.0
        # Square Buildings
        # buildings = [ (-1.5, -0.2), (-1.5, -2.0), (-3.0, -1.0), (-3.0, 1.0) ]
        buildings = [ (-1.5, -0.2), (-3.0, -1.5), (-3.0, 1.5) ]
        for x,y in buildings:
            p.loadURDF("./buildings/building_square.urdf",
                       [x, y, 1.05],
                       p.getQuaternionFromEuler([0, 0, 0.7]),
                       globalScaling=scaling_factor,
                       physicsClientId=physicsClientId
                       )
        # Hexagonal Buildings
        p.loadURDF("./buildings/building_hexa_50_200.urdf",
                       [0.5, 0.5, 0.05],
                       p.getQuaternionFromEuler([0, 0, 0]),
                       globalScaling=scaling_factor,
                       physicsClientId=physicsClientId
                       )
        p.loadURDF("./buildings/building_hexa_50_150.urdf",
                       [0.50, 3.0, 0.05],
                       p.getQuaternionFromEuler([0, 0, 0]),
                       globalScaling=scaling_factor,
                       physicsClientId=physicsClientId
                       )
        p.loadURDF("./buildings/building_hexa_50_120.urdf",
                       [2.50, 2.0, 0.05],
                       p.getQuaternionFromEuler([0, 0, 0]),
                       globalScaling=scaling_factor,
                       physicsClientId=physicsClientId
                       )
        # Right and Left Strange Buildings
        p.loadURDF("./buildings/building_right_120.urdf",
                       [3.25, -1.2, 0.0],
                       p.getQuaternionFromEuler([0, 0, 0]),
                       globalScaling=scaling_factor,
                       physicsClientId=physicsClientId
                       )
        p.loadURDF("./buildings/building_left_120.urdf",
                       [1.25, -1.2, 0.0],
                       p.getQuaternionFromEuler([0, 0, 0]),
                       globalScaling=scaling_factor,
                       physicsClientId=physicsClientId
                       )

    if version == 101 :
        scaling_factor = 1.0
        p.loadURDF("./buildings/building_hexa_50_200.urdf",
                       [-2.0, -2.0, 0.05],
                       p.getQuaternionFromEuler([0, 0, 0]),
                       globalScaling=scaling_factor,
                       physicsClientId=physicsClientId
                       )

