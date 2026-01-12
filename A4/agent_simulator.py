"""
Assignment 4: Agent-Based Model for Surface Panelization
Author: Julius Drejer Mosgaard

Agent Simulator Template

Description:
This file defines the structural outline for stepping and visualizing
agents within Grasshopper. No simulation logic is implemented. All behavior
(update, responding to signals, movement, etc.) must be
implemented inside your Agent class in `agent_builder.py`.

Note: This script is intended to be used within Grasshopper's Python
scripting component.
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

# ---------- Inputs: AgentKey (string) ----------
# S, Step, Rep, Run, Reset

P_out = []
N_out = []
C = []

# Resolve the sticky key:
key = None
if Builder and hasattr(Builder, "InstanceGuid"):
    key = "agents_curv_" + str(Builder.InstanceGuid)
elif AgentKey:
    key = AgentKey

if S is None:
    ghenv.Component.AddRuntimeMessage(
        gh.Kernel.GH_RuntimeMessageLevel.Error,
        "Input S is null – please connect the Surface."
    )
elif not key:
    ghenv.Component.AddRuntimeMessage(
        gh.Kernel.GH_RuntimeMessageLevel.Warning,
        "No Builder component or AgentKey provided. Connect the Builder component or pass AgentKey."
    )
else:
    # Safe sticky lookup
    pts_state = sc.sticky.get(key, None)
    if pts_state is None:
        # Nothing stored yet: nothing to simulate
        ghenv.Component.AddRuntimeMessage(
            gh.Kernel.GH_RuntimeMessageLevel.Warning,
            "No agent data found in sticky for key: {}".format(key)
        )
        pts_state = []

    # Convert to Point3d list
    pts_state = [rg.Point3d(p) for p in pts_state]

    # Optionally Reset from current builder input points (if Reset true, allow builder to reinitialize)
    if Reset and Builder:
        sc.sticky[key] = [rg.Point3d(p) for p in pts_state]

    # Precompute UV step sizes
    u_dom = S.Domain(0)
    v_dom = S.Domain(1)
    step_factor = Step if Step is not None else 0.2
    base_frac = 0.05
    du_step = (u_dom.T1 - u_dom.T0) * base_frac * step_factor
    dv_step = (v_dom.T1 - v_dom.T0) * base_frac * step_factor

    # Repulsion clamp
    rep_strength = Rep if Rep is not None else 0.0
    rep_strength = max(0.0, min(1.0, rep_strength))

    # If Run True -> perform one iteration
    if Run:
        count = len(pts_state)
        # estimate typical neighbor distance
        min_dists = []
        for i in range(count):
            pi = pts_state[i]
            min_d = System.Double.MaxValue
            for j in range(count):
                if i == j: continue
                pj = pts_state[j]
                d = pi.DistanceTo(pj)
                if d < min_d:
                    min_d = d
            if min_d < System.Double.MaxValue:
                min_dists.append(min_d)

        if min_dists:
            typical = median(min_dists)
            rep_radius = typical * 1.5
        else:
            typical = 0.0
            rep_radius = 0.0

        new_pts = []
        new_C_vals = []

        for i, pt in enumerate(pts_state):
            ok, u, v = S.ClosestPoint(pt)
            if not ok:
                new_pts.append(pt)
                new_C_vals.append(0.0)
                continue

            c0 = gaussian_curv(S, u, v)
            best_u, best_v = u, v
            best_c = c0

            candidates = [
                (u + du_step, v),
                (u - du_step, v),
                (u, v + dv_step),
                (u, v - dv_step),
            ]
            for u1, v1 in candidates:
                u1 = clamp_param(u1, u_dom)
                v1 = clamp_param(v1, v_dom)
                c1 = gaussian_curv(S, u1, v1)
                if c1 > best_c:
                    best_c = c1
                    best_u = u1
                    best_v = v1

            curv_pt = S.PointAt(best_u, best_v)

            # Repulsion
            rep_vec = rg.Vector3d(0, 0, 0)
            if rep_strength > 0.0 and rep_radius > 0.0:
                for j, pj in enumerate(pts_state):
                    if j == i: continue
                    d = curv_pt.DistanceTo(pj)
                    if d <= 1e-8 or d > rep_radius: continue
                    dir_v = curv_pt - pj
                    if dir_v.IsZero: continue
                    dir_v.Unitize()
                    w = (rep_radius - d) / rep_radius
                    rep_vec += dir_v * w

                if not rep_vec.IsZero:
                    rep_vec.Unitize()
                    rep_step_len = typical * 0.5 * rep_strength
                    rep_vec *= rep_step_len

            candidate_pt = curv_pt + rep_vec

            ok2, u2, v2 = S.ClosestPoint(candidate_pt)
            if ok2:
                final_pt = S.PointAt(u2, v2)
                final_c = gaussian_curv(S, u2, v2)
            else:
                final_pt = candidate_pt
                final_c = best_c

            new_pts.append(final_pt)
            new_C_vals.append(final_c)

        # Write back new state into sticky
        sc.sticky[key] = [rg.Point3d(p) for p in new_pts]
        pts_state = new_pts
        C_vals = new_C_vals
    else:
        # Not running: just report current
        C_vals = []
        for p in pts_state:
            ok, u, v = S.ClosestPoint(p)
            C_vals.append(gaussian_curv(S, u, v) if ok else 0.0)

    # Build outputs
    P_out = [rg.Point3d(p) for p in pts_state]
    N_out = []
    for p in P_out:
        ok, u, v = S.ClosestPoint(p)
        if ok:
            n = S.NormalAt(u, v)
            if not n.IsZero: n.Unitize()
            N_out.append(n)
        else:
            N_out.append(rg.Vector3d(0,0,0))
    C = C_vals
