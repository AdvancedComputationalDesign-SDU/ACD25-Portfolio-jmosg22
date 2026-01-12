"""
Assignment 4: Agent-Based Model for Surface Panelization

Author: Julius Drejer Mosgaard

Surface Generator Template

Description:
This file defines the structural outline for generating or preprocessing
surfaces and geometric signal fields for Assignment 4.

Note: This script is intended to be used within Grasshopper's Python
scripting component.
"""

import Rhino
import numpy as np

# Basic validation
if U is None or V is None or U < 2 or V < 2:
    S = None
else:
    # Defaults if optional inputs are missing
    if ZVar is None:
        ZVar = 1.0          # max |z| ~ ZVar
    if ExtU is None:
        ExtU = 1.0          # extent in U (X direction)
    if ExtV is None:
        ExtV = 1.0          # extent in V (Y direction)

    # NumPy random generator with seed
    rng = np.random.default_rng(Seed)

    # Degrees must be < number of points in each direction
    deg_u = min(3, U - 1)
    deg_v = min(3, V - 1)

    # Create coordinates using NumPy
    u_coords = np.linspace(0.0, ExtU, U)    # length U
    v_coords = np.linspace(0.0, ExtV, V)    # length V

    # Meshgrid: X, Y have shape (V, U)
    X, Y = np.meshgrid(u_coords, v_coords, indexing='xy')

    # Random Z values in [-ZVar, ZVar], shape (V, U)
    Z = (rng.random((V, U)) * 2.0 - 1.0) * ZVar

    # Flatten in V-major, U-minor order:
    X_flat = X.ravel(order='C')
    Y_flat = Y.ravel(order='C')
    Z_flat = Z.ravel(order='C')

    # Build list of Point3d for CreateThroughPoints
    pts = [
        Rhino.Geometry.Point3d(float(x), float(y), float(z))
        for x, y, z in zip(X_flat, Y_flat, Z_flat)
    ]

    # Create NURBS surface through the points
    S = Rhino.Geometry.NurbsSurface.CreateThroughPoints(
        pts,
        U,          # point count in U
        V,          # point count in V
        deg_u,      # degree in U
        deg_v,      # degree in V
        False,      # not periodic in U
        False       # not periodic in V
    )