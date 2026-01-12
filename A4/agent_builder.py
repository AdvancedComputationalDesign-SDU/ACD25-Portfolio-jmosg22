"""
Assignment 4: Agent-Based Model for Surface Panelization

Author: Julius Drejer Mosgaard

Agent Builder Template

Description:
Defines the core Agent class and factory methods for constructing an
agent-based system. Provides a high-level OOP structure for sensing,
decision-making, and movement, along with a stateful Grasshopper
GH_ScriptInstance example.

Note: This script is intended to be used within Grasshopper's Python
scripting component.

Inputs:
    S: Surface to divide (Surface or Brep)
    P: Initial grid points (List of Point3d)
    Reset: Boolean to reset points to input P (Boolean)
    Step: Step size for agent movement (Number)
    Rep: Repulsion distance (Number)

Outputs:
    P_out: Current agent positions (List of Point3d)
    N_out: Surface normals at agent positions (List of Vector3d)
    C: Gaussian curvature at agent positions (List of Number)
    AgentKey: Unique key for sticky storage (String)
    BuilderComp: Reference to this GH component (GH_Component)
"""

import Rhino.Geometry as rg
import scriptcontext as sc
import Grasshopper as gh
import System

# ---------- Helpers ----------
def clamp_param(t, dom):
    if t < dom.T0: return dom.T0
    if t > dom.T1: return dom.T1
    return t

def gaussian_curv(surf, u, v):
    try:
        c = surf.CurvatureAt(u, v)
    except:
        return 0.0
    if c is None:
        return 0.0
    return abs(c.Gaussian)

def median(values):
    if not values:
        return 0.0
    vals = sorted(values)
    n = len(vals)
    mid = n // 2
    if n % 2 == 1:
        return vals[mid]
    else:
        return 0.5 * (vals[mid - 1] + vals[mid])

# ---------- Inputs available from GH component ----------
# S, P, Reset, Step, Rep

# Outputs to fill:
P_out = []
N_out = []
C = []
AgentKey = None
BuilderComp = None

# Safety checks
if S is None:
    ghenv.Component.AddRuntimeMessage(
        gh.Kernel.GH_RuntimeMessageLevel.Error,
        "Input S is null – please connect a Surface."
    )
else:
    # Build unique sticky key per builder component instance
    key_pts = "agents_curv_" + str(ghenv.Component.InstanceGuid)
    AgentKey = key_pts
    BuilderComp = ghenv.Component 

    # Input points (allow None)
    pts_in = list(P) if P else []

    # If Reset requested -> overwrite sticky with input points
    if Reset:
        sc.sticky[key_pts] = [rg.Point3d(pt) for pt in pts_in]

    # Ensure sticky exists and contains a list of Point3d
    sticky_pts = sc.sticky.get(key_pts, None)
    if sticky_pts is None or not isinstance(sticky_pts, (list, tuple)):
        sc.sticky[key_pts] = [rg.Point3d(pt) for pt in pts_in]
        sticky_pts = sc.sticky[key_pts]

    # If counts mismatch (for example P changed) reinitialize sticky to input points
    if len(sticky_pts) != len(pts_in):
        sc.sticky[key_pts] = [rg.Point3d(pt) for pt in pts_in]
        sticky_pts = sc.sticky[key_pts]

    # outputs: current positions, normals, curvature
    P_out = [rg.Point3d(p) for p in sticky_pts]

    N_out = []
    C_vals = []
    for p in P_out:
        ok, u, v = S.ClosestPoint(p)
        if not ok:
            N_out.append(rg.Vector3d(0,0,0))
            C_vals.append(0.0)
            continue
        n = S.NormalAt(u, v)
        if not n.IsZero: n.Unitize()
        N_out.append(n)
        C_vals.append(gaussian_curv(S, u, v))

    C = C_vals