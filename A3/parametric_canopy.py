"""
Assignment 3: Parametric Structural Canopy — Pseudocode Scaffold

Author: Julius Drejer Mosgaard

    This file is a **high-level pseudocode**.
    It outlines the pipeline and function responsibilities. 
    Use it as a guide and fill in the bodies with your own logic.
"""

# NUMPY
import numpy as np
import matplotlib.pyplot as plt

# array dimensions
height = 100
width = 100

# prepare canvas
canvas = np.zeros((height, width, 3), dtype=float)

# choose 2 colors:
# 1) edge color (both left + right)
# 2) center/sine curve color

color_options = {
    "red":   (255, 0, 0),
    "blue":  (0, 0, 255),
}

edge_color = color_options["blue"]
center_color = color_options["red"]

# parameters of sine wave
amplitude = 40
frequency = 5 * np.pi / height

# y-coordinates
y = np.arange(height)

# sine x-position for each row
sine_middle = (width / 2) + amplitude * np.sin(frequency * y)
sine_middle = sine_middle[:, None]  # shape (height, 1)

# x-coordinates
x = np.arange(width)

# distance from sine curve
distance = np.abs(x - sine_middle)

# normalize distance to 0–1
t = distance / (width / 2)
t = np.clip(t, 0, 1)
t_expanded = t[..., None]

# blend between center_color and edge_color
canvas[:] = (1 - t_expanded) * center_color + t_expanded * edge_color

# draw image
plt.imshow(canvas.astype(np.uint8))
plt.axis("off")
plt.savefig("images/surfaceimg3.png", bbox_inches='tight', pad_inches=0)
plt.close()

# GRASSHOPPER
### Format
# ------------------- TITLE OF PYTHON3 COMPONENT ---------------
# Subtitle inside python component


# -------------------- IMAGE TO POINTS TO SURFACE --------------------
import Rhino
import System
from System.Drawing import Bitmap, Imaging
from System.Runtime.InteropServices import Marshal
import Rhino.Geometry as rg
import scriptcontext as sc

# Read the image
if isinstance(Image, str):
    bmp = Bitmap(Image)
elif isinstance(Image, Bitmap):
    bmp = Image
else:
    raise ValueError("Input 'Image' must be a file path or a Bitmap.")

width  = bmp.Width
height = bmp.Height

W = width
H = height

# Lock bitmap and copy rawdata
rect = System.Drawing.Rectangle(0, 0, width, height)
bmpdata = bmp.LockBits(rect, Imaging.ImageLockMode.ReadOnly, Imaging.PixelFormat.Format24bppRgb)

stride = bmpdata.Stride
byte_count = stride * height

buf = System.Array.CreateInstance(System.Byte, byte_count)
Marshal.Copy(bmpdata.Scan0, buf, 0, byte_count)

bmp.UnlockBits(bmpdata)

# Downsampling grid size by U x V input
U = int(U)
V = int(V)

# Evenly spaced sampling positions across the image
x_steps = [i * (width - 1) / (int(U) - 1) for i in range(int(U))]
y_steps = [i * (height - 1) / (int(V) - 1) for i in range(int(V))]

Pts = []

# Sample each image RGB value and convert to xyz coordinate. (x,y is location, z is height)
for y in y_steps:
    yi = int(y)
    row_offset = yi * stride

    for x in x_steps:
        xi = int(x)
        base = row_offset + xi * 3

        B = buf[base]
        G = buf[base + 1]
        R = buf[base + 2]

        # Avoiding high z-value as colour codes are more prevalent, and adding a scale factor.
        Z = (0.2126 * R + 0.7152 * G + 0.0722 * B) * ScaleZ

        Pts.append(Rhino.Geometry.Point3d(float(x), float(y), float(Z)))

        

real_pts = []

for p in Pts:
    if isinstance(p, rg.Point3d):
        # Already correct
        real_pts.append(p)

    elif isinstance(p, rg.Point):
        # Grasshopper Point geometry
        real_pts.append(p.Location)

    elif isinstance(p, Rhino.DocObjects.PointObject):
        # A Rhino doc point object
        real_pts.append(p.Geometry.Location)

    elif isinstance(p, System.Guid):
        # GUID → retrieve Rhino object → convert to Point3d
        rh_obj = sc.doc.Objects.Find(p)
        if rh_obj and hasattr(rh_obj.Geometry, "Location"):
            real_pts.append(rh_obj.Geometry.Location)
        else:
            raise TypeError("Guid does not refer to a point.")

    else:
        raise TypeError("Unsupported point type: {}".format(type(p)))

# pts: list of Rhino.Geometry.Point3d
# U: U count
# interpolate: boolean

# Convert the flat list into a 2D point grid.
V = len(real_pts) // U

# Reshape flat list into UV grid
point_grid = []
for v in range(V):
    row = []
    for u in range(U):
        row.append(real_pts[v * U + u])
    point_grid.append(row)

# Create the surface
if interpolate:
    # Interpolated surface (more precise)
    srf = rg.NurbsSurface.CreateThroughPoints(point_grid, U, V, 3, 3, False, False)
else:
    # Least squares surface (same method GH uses when 'Interpolate' = False)
    srf = rg.NurbsSurface.CreateFromPoints(real_pts, U, V, 3, 3)

# Output
a = srf

# -------------------- POINTS FOR SUPPORTS PLACEMENT --------------------
import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino.Geometry as rg
import math


# Convert GUID to real geometry
srf_obj = rs.coercesurface(srf)
if srf_obj is None:
    brep = rs.coercebrep(srf)
    if brep:
        srf_obj = brep.Faces[0].ToNurbsSurface()
    else:
        raise Exception("Input is not a surface or brep.")


# Sample surface points and normals

pts = []
normals = []
zs = []

dom_u = srf_obj.Domain(0)
dom_v = srf_obj.Domain(1)

for i in range(Ucount):
    for j in range(Vcount):
        # correct UV parameters
        u = dom_u.ParameterAt(float(i)/(Ucount-1))
        v = dom_v.ParameterAt(float(j)/(Vcount-1))

        pt = srf_obj.PointAt(u, v)
        n = srf_obj.NormalAt(u, v)
        n.Unitize()

        pts.append(pt)
        normals.append(n)
        zs.append(pt.Z)


# Detect lowest flat areas

min_z = min(zs)

# tolerances 
z_tolerance = 0.5          # points within 0.5 units of lowest Z  
angle_tol = math.radians(3)  # normals within 3° considered flat

# average normal among lowest 5% of points
count_5 = max(1, int(len(pts) * 0.05))
lowest_indices = sorted(range(len(zs)), key=lambda i: zs[i])[:count_5]

avg_n = rg.Vector3d(
    sum(normals[i].X for i in lowest_indices) / count_5,
    sum(normals[i].Y for i in lowest_indices) / count_5,
    sum(normals[i].Z for i in lowest_indices) / count_5
)
avg_n.Unitize()

flat_low_points = []

for pt, n, z in zip(pts, normals, zs):
    # correct parallel test
    if n.IsParallelTo(avg_n, angle_tol) != 0:
        if abs(z - min_z) <= z_tolerance:
            flat_low_points.append(pt)

--
# Cluster flat regions spatially

clusters = []
used = set()

def dist(a,b): return a.DistanceTo(b)

# merge points from same flat region
bbox = srf_obj.GetBoundingBox(True)
cluster_tol = bbox.Diagonal.Length * region_tol

for i, p in enumerate(flat_low_points):
    if i in used: continue
    group = [p]
    used.add(i)

    for j, q in enumerate(flat_low_points):
        if j in used: continue
        if dist(p, q) < cluster_tol:
            group.append(q)
            used.add(j)
    clusters.append(group)


# Compute centroid of each region

centers = []

for group in clusters:
    x = sum(p.X for p in group) / len(group)
    y = sum(p.Y for p in group) / len(group)
    z = sum(p.Z for p in group) / len(group)
    centers.append(rg.Point3d(x, y, z))

# -------------------- GENERATE SUPPORTS --------------------
import rhinoscriptsyntax as rs
import random
import Rhino
import math
from collections import defaultdict

# Inputs:
# pts = list of base points where trees must grow
# height, gen, angle, L, s

Lines = []

def Grow(pt, v, length, g):
    if g < gen:
        plane = rs.PlaneFromNormal(pt, v)
        random_pt = rs.EvaluatePlane(plane, [random.uniform(-1, 1), random.uniform(-1, 1)])
        rot_axis = rs.VectorCreate(random_pt, pt)
    
        V1 = rs.VectorRotate(v, random.uniform(-angle, 0), rot_axis)
        pt1 = rs.PointAdd(pt, rs.VectorScale(V1, length))

        m1 = [pt[0], pt[1], pt[2] + (pt1[2] - pt[2]) * 0.5]
        m2 = [pt1[0], pt1[1], pt[2] + (pt1[2] - pt[2]) * 0.5]

        V2 = rs.VectorRotate(v, random.uniform(0, angle), rot_axis)
        pt2 = rs.PointAdd(pt, rs.VectorScale(V2, length))
        
        m3 = [pt[0], pt[1], pt[2] + (pt2[2] - pt[2]) * 0.5]
        m4 = [pt2[0], pt2[1], pt[2] + (pt2[2] - pt[2]) * 0.5]

        L1 = rs.AddCurve([pt, m1, m2, pt1])
        L2 = rs.AddCurve([pt, m3, m4, pt2])

        Lines.append(L1)
        Lines.append(L2)
        
        Grow(pt1, V1, length * random.uniform(0.75, 0.95), g + 1)
        Grow(pt2, V2, length * random.uniform(0.75, 0.95), g + 1)

random.seed(s)

# Vector amplitude controlled by height
V = [0, 0, height]

# Points for supports
for pt in pts:
    B = rs.PointAdd(pt, rs.VectorScale(V, L))  # first branch
    Lines.append(rs.AddLine(pt, B))
    Grow(B, V, L, 0)

# Output
trees = Lines

# ------------------------- CUT SUPPORTS AT SURFACE ------------------------
import rhinoscriptsyntax as rs
import Rhino
import Rhino.Geometry as rg
import scriptcontext as sc

# Convert input surface to real geometry
geo = rs.coercegeometry(srf)
if isinstance(geo, rg.Brep):
    srf_obj = geo.Faces[0].ToNurbsSurface()
elif isinstance(geo, rg.Surface):
    srf_obj = geo.ToNurbsSurface()
else:
    raise Exception("Input srf must be a surface or brep.")

# Convert all lines to actual geometry
lines_list = []
for l in lines:
    crv = rs.coercecurve(l)
    if crv:
        lines_list.append(crv)


# Move the surface upward by srf_z


xf = rg.Transform.Translation(0, 0, srf_z)
srf_moved = srf_obj.Duplicate()
srf_moved.Transform(xf)


# Intersect and trim each line

lines_cut = []

for crv in lines_list:

    # Get intersection with surface
    results = rg.Intersect.Intersection.CurveSurface(
        crv, srf_moved, 0.001, 0.001
    )

    if results and results.Count > 0:
        # take first intersection
        inter = results[0]
        t = inter.ParameterA
        pt = crv.PointAt(t)

        # Only keep the segment from start → intersection
        trimmed_curve = rg.Line(crv.PointAtStart, pt).ToNurbsCurve()
        lines_cut.append(trimmed_curve)

    else:
        # Check the end point
        start = crv.PointAtStart
        end = crv.PointAtEnd

        # Evaluate surface at projection of line start
        # Here we assume Z height is what matters
        if start.Z < srf_moved.GetBoundingBox(True).Max.Z:
            lines_cut.append(crv)
        # if line is fully above → ignore it completely


# Outputs

srf_out = srf_moved

# -------------------- CULL SUPPORTS ABOVE SURFACE --------------------
import rhinoscriptsyntax as rs
import Rhino.Geometry as rg

# Convert surface input


geo = rs.coercegeometry(srf)
if isinstance(geo, rg.Brep):
    srf_obj = geo.Faces[0]
elif isinstance(geo, rg.Surface):
    srf_obj = geo
else:
    raise Exception("Input srf must be a surface or brep.")


# Distance of a point to a surface


def signed_distance(pt, surface):
    # Closest point on surface
    rc, u, v = surface.ClosestPoint(pt)
    if not rc:
        return None

    pt_on_srf = surface.PointAt(u, v)

    # Surface normal at closest point
    n = surface.NormalAt(u, v)
    n.Unitize()

    # Vector from surface to point
    vpt = pt - pt_on_srf

    # Signed distance = dot(normal, vector)
    return rg.Vector3d.Multiply(n, vpt)

# Process curves

crvs_out = []

for c in crvs:
    crv = rs.coercecurve(c)
    if not crv:
        continue

    # Take midpoint of curve
    t_mid = crv.Domain.Mid
    pt_mid = crv.PointAt(t_mid)

    d = signed_distance(pt_mid, srf_obj)
    if d is None:
        continue

    # Boolean decides which side to keep
    if side:      # True → keep ABOVE
        if d > 0:
            crvs_out.append(crv)
    else:         # False → keep BELOW
        if d < 0:
            crvs_out.append(crv)

# Output

curves_out = crvs_out

# --------------------VARIABLE PIPING OF CRVS--------------------------

# Inputs:
#   crvs   : list (curve GUIDs or Rhino.Geometry.Curve)
#   factor : float                                     
#
# Outputs:
#   pipes         : list of Breps (piped curves)

import rhinoscriptsyntax as rs
import Rhino.Geometry as rg
import scriptcontext as sc
import math
from System.Collections.Generic import List

#  prepare outputs 
pipes = []
weave_radii = []
radii_end = []
radii_start = []

# safe coercion of incoming curves (handles GUIDs)
geo_crvs = []
for c in crvs:
    try:
        cc = rs.coercecurve(c)   # returns None if not a curve
    except Exception:
        cc = None
    geo_crvs.append(cc)

# collect all start/end Z values 
z_values = []
for c in geo_crvs:
    if c is None:
        continue
    sp = c.PointAtStart
    ep = c.PointAtEnd
    z_values.append(sp.Z)
    z_values.append(ep.Z)

# If no valid curves, leave outputs empty
if not z_values:
    # pipes, radii_start, radii_end, weave_radii remain empty lists
    pass
else:
    # Domain end value (max Z) -- emulates Deconstruct Domain -> End
    z_max = max(z_values)

    # guard against z_max == 0 (avoid division by zero)
    if abs(z_max) < 1e-12:
        z_max = 1.0

    # compute normalization streams: (z_max - z) / z_max
    norm_start = []
    norm_end   = []

    for c in geo_crvs:
        if c is None:
            norm_start.append(0.0)
            norm_end.append(0.0)
            continue
        sp = c.PointAtStart
        ep = c.PointAtEnd
        n0 = (z_max - sp.Z) / z_max
        n1 = (z_max - ep.Z) / z_max
        norm_start.append(n0)
        norm_end.append(n1)

   # Python code emulation of the Weave (weave start & end into a single stream)

    woven = [[s, e] for s, e in zip(norm_start, norm_end)]

    # multiply by factor (the multiplication component after the weave)
    # this yields the final radii used by Pipe Variable
    for pair in woven:
        r0 = max(pair[0] * factor, 0.0)
        r1 = max(pair[1] * factor, 0.0)
        weave_radii.append([r0, r1])
        radii_start.append(r0)
        radii_end.append(r1)

    # Now create pipes: curves are reparameterized and grafted (like in the grasshopper component "Pipe Variable")
    try:
        tol = sc.doc.ModelAbsoluteTolerance
    except Exception:
        tol = 0.01

    ang_tol = math.radians(1.0)  # 1 degree in radians

    for c, (r0, r1) in zip(geo_crvs, weave_radii):
        if c is None:
            pipes.append(None)
            continue

        # duplicate curve before changing parameterization
        try:
            crv = c.DuplicateCurve()
        except Exception:
            crv = c

        # reparameterize to 0..1 (like the Reparameterize in grasshopper)
        try:
            crv.Reparameterize(0.0, 1.0)
        except Exception:
            # if Reparameterize isn't available/allowed, ignore
            pass

        # parameters list per curve: multi-line list of 0 and 1 (emulates Pipe Variable "parameters" multi-list)
        params_dotnet = List[float]([0.0, 1.0])
        radii_dotnet  = List[float]([float(r0), float(r1)])

        # If either radius is zero, CreatePipe may still return a pipe depending on curve; keep values >= 0
        try:
            # correct overload with angleToleranceRadians included
            breps = rg.Brep.CreatePipe(
                crv,
                params_dotnet,
                radii_dotnet,
                False,                    # cap (False = open)
                rg.PipeCapMode.Flat,     # cap mode (Flat/Round)
                True,                     # fit rail
                tol,                      # tolerance
                ang_tol                   # angle tolerance in radians
            )
        except Exception:
            breps = None

        if breps and len(breps) > 0:
            pipes.append(breps[0])
        else:
            pipes.append(None)


# ------------------------- TESSELATE SURFACE -------------------------
import Rhino.Geometry as rg
import math

# Input cleaning 
if isinstance(S, rg.Brep):
    surf = S.Faces[0].ToNurbsSurface()
elif isinstance(S, rg.Surface):
    surf = S.ToNurbsSurface()
else:
    raise ValueError("Input must be Brep or Surface")

angle_tol = math.radians(MaxAngle)

u_dom = surf.Domain(0)
v_dom = surf.Domain(1)


# Helpers 
def normal_angle(n1, n2):
    dot = max(-1.0, min(1.0, n1*n2))
    return math.acos(dot)

def patch_min_edge_length(pts):
    return min((pts[i].DistanceTo(pts[(i+1)%4]) for i in range(4)))


# Recursive subdivision
patches = []
boundaries = []


def subdivide(u0, u1, v0, v1, depth):

    # Sample points
    pts_uv = [
        (u0, v0),
        (u1, v0),
        (u1, v1),
        (u0, v1),
        ((u0+u1)*0.5, (v0+v1)*0.5)
    ]

    pts = [surf.PointAt(u, v) for (u, v) in pts_uv]
    normals = [surf.NormalAt(u, v) for (u, v) in pts_uv]

    # Stop if patch is too small
    if patch_min_edge_length(pts[:4]) < MinSize:
        small = True
    else:
        small = False

    # Compute normal allignment
    max_diff = 0.0
    for i in range(5):
        for j in range(i+1, 5):
            ang = normal_angle(normals[i], normals[j])
            if ang > max_diff:
                max_diff = ang

    # Stop if angle OK or patch too small or depth limit
    if max_diff <= angle_tol or small or depth >= MaxDepth:
        m = rg.Mesh()

        idx = []
        for (u, v) in [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]:
            idx.append(m.Vertices.Add(surf.PointAt(u, v)))

        m.Faces.AddFace(idx[0], idx[1], idx[2], idx[3])
        m.Normals.ComputeNormals()
        patches.append(m)

        boundaries.append(
            rg.Polyline([pts[0], pts[1], pts[2], pts[3], pts[0]])
        )
        return

    # If not subdivide into 4
    um = (u0 + u1)*0.5
    vm = (v0 + v1)*0.5

    subdivide(u0, um, v0, vm, depth+1)
    subdivide(um, u1, v0, vm, depth+1)
    subdivide(u0, um, vm, v1, depth+1)
    subdivide(um, u1, vm, v1, depth+1)


# Start
subdivide(u_dom.T0, u_dom.T1, v_dom.T0, v_dom.T1, 0)


# Output 
Patches = patches
Edges = boundaries

# --------------- CONVERT MESH TO A BREP AND OFFSET ----------------
import Rhino
import Rhino.Geometry as rg
import scriptcontext as sc
import rhinoscriptsyntax as rs
import System
import math

# INPUT: M  -> a mesh, list of meshes, GUIDs, or ObjRefs
# OUTPUT: FacesPts (list of lists of Point3d), Surfaces (list of Breps)

def resolve_mesh(obj):
    """Try to return a Rhino.Geometry.Mesh from various possible inputs:
       - actual Mesh
       - Rhino.DocObjects.ObjRef
       - System.Guid (object id)
       - Rhino object from RhinoCommon
    Returns None if it couldn't resolve a mesh.
    """
    if obj is None:
        return None

    # already a Mesh
    if isinstance(obj, rg.Mesh):
        return obj

    # Rhino ObjRef
    try:
        if isinstance(obj, Rhino.DocObjects.ObjRef):
            geom = obj.Geometry()
            if isinstance(geom, rg.Mesh):
                return geom
            # Some geometry may be a Brep with a mesh representation:
            if isinstance(geom, rg.Brep):
                # try get a mesh from Brep (meshes of brep faces)
                m = rg.Mesh()
                if rg.Mesh.CreateFromBrep(geom, rg.MeshingParameters.Default, m):
                    return m
    except Exception:
        pass

    # GUID (System.Guid) or string representation of id
    try:
        if isinstance(obj, System.Guid) or isinstance(obj, str):
            # find by id in document
            found = sc.doc.Objects.Find(obj)
            if found:
                geom = found.Geometry
                if isinstance(geom, rg.Mesh):
                    return geom
                if isinstance(geom, rg.Brep):
                    m = rg.Mesh()
                    if rg.Mesh.CreateFromBrep(geom, rg.MeshingParameters.Default, m):
                        return m
    except Exception:
        pass

    # sometimes Grasshopper passes wrappers with .Geometry or .Object
    try:
        if hasattr(obj, "Geometry"):
            geom = obj.Geometry
            if isinstance(geom, rg.Mesh):
                return geom
            if isinstance(geom, rg.Brep):
                m = rg.Mesh()
                if rg.Mesh.CreateFromBrep(geom, rg.MeshingParameters.Default, m):
                    return m
    except Exception:
        pass

    # last attempt: if it has Faces and Vertices attributes, treat as mesh-like
    try:
        if hasattr(obj, "Faces") and hasattr(obj, "Vertices"):
            # assume it's mesh-like
            return obj
    except Exception:
        pass

    return None


# Ensure M is a list
mesh_inputs = M if isinstance(M, (list, tuple)) else [M]

FacesPts = []
Surfaces = []

for mi in mesh_inputs:
    mesh = resolve_mesh(mi)
    if mesh is None:
        # skip non-resolvable inputs
        continue

    # ensure mesh has correct topology/normals
    try:
        mesh.Normals.ComputeNormals()
    except Exception:
        pass

    # iterate faces
    for f in mesh.Faces:
        # get vertex indices for the face (quad or triangle)
        if f.IsQuad:
            ids = [f.A, f.B, f.C, f.D]
        else:
            # triangle -> duplicate last vertex so we have 4 points
            ids = [f.A, f.B, f.C, f.C]

        # collect 3D points (Point3d)
        try:
            pts = [rg.Point3d(mesh.Vertices[i]) for i in ids]
        except Exception:
            # if indexing fails, skip this face
            continue

        FacesPts.append(pts)

        # attempt to create planar Brep from corner points
        try:
            brep = rg.Brep.CreateFromCornerPoints(pts[0], pts[1], pts[2], pts[3], sc.doc.ModelAbsoluteTolerance)
        except Exception:
            brep = None

        # If CreateFromCornerPoints failed (non-planar), try making a ruled surface:
        if brep is None:
            try:
                # create a surface via lofting the two edge curves
                crv1 = rg.LineCurve(pts[0], pts[1])
                crv2 = rg.LineCurve(pts[3], pts[2])
                loft = rg.Brep.CreateFromLoft([crv1, crv2], rg.Point3d.Unset, rg.Point3d.Unset, rg.LoftType.Normal, False)
                if loft:
                    brep = loft[0]
            except Exception:
                brep = None

        if brep is not None:
            Surfaces.append(brep)

cbrep = rs.coercebrep(brep)
tol = sc.doc.ModelAbsoluteTolerance

b = Rhino.Geometry.Brep.CreateOffsetBrep(cbrep, dist, solid, ext, tol)

brep_off = b[0]

# ---------------------- FINAL CANOPY -------------
# Output from the offset and the pipe variable is then the final structure.