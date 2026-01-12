"""
Assignment 2: Fractal Generator

Author: Julius Drejer Mosgaard

Description:
This script generates a simple fractal triangle pattern using recursive functions
"""
import math
import random
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
from shapely.affinity import rotate
import matplotlib.colors as mcolors

# Global list to store line segments
line_list = []

# Interpolation function between two colours
def color(c1, c2, t):
    return (
        c1[0] + (c2[0] - c1[0]) * t,
        c1[1] + (c2[1] - c1[1]) * t,
        c1[2] + (c2[2] - c1[2]) * t,
    )

# Define triangle function
def triangle(start_pos, initial_length, depth, max_depth, rotation_step):
    if depth > max_depth:
        return

    # Calculate the vertices of the triangle
    A = start_pos
    B = (start_pos[0] + initial_length, start_pos[1])
    C = (start_pos[0] + initial_length / 2, start_pos[1] + (math.sqrt(3) / 2) * initial_length)

    # Create a polygon for the triangle
    tri = Polygon([A, B, C, A])

    # Rotate each triangle by depth * rotation_step
    if rotation_step != 0:
        tri = rotate(tri, depth * rotation_step, origin='centroid')

    # Store (triangle, depth)
    line_list.append((tri, depth))

    # Stop if we've reached the maximum recursion depth
    if depth == max_depth:
        return

    # Recursive calls for smaller triangles
    AB_mid = ((A[0] + B[0]) / 2, (A[1] + B[1]) / 2)
    BC_mid = ((B[0] + C[0]) / 2, (B[1] + C[1]) / 2)
    CA_mid = ((C[0] + A[0]) / 2, (C[1] + A[1]) / 2)

    # Pass rotation_step so next levels keep rotating more
    triangle(A, initial_length / 2, depth + 1, max_depth, rotation_step)
    triangle(AB_mid, initial_length / 2, depth + 1, max_depth, rotation_step)
    triangle(CA_mid, initial_length / 2, depth + 1, max_depth, rotation_step)

# Visualization function
def visualize_fractal(line_list, min_depth, max_depth, color_start, color_end, outlines=False):
    plt.figure(figsize=(10, 10))

    c0 = mcolors.to_rgb(color_start)
    c1 = mcolors.to_rgb(color_end)

    for item in line_list:
        if isinstance(item, tuple) and len(item) == 2:
            tri, depth = item
        else:
            tri = item
            depth = 0

        x, y = tri.exterior.xy
        denom = max(1, (max_depth - min_depth))
        t = (depth - min_depth) / denom
        t = max(0.0, min(1.0, t))
        col = color(c0, c1, t)

        if outlines:
            plt.plot(x, y, color=col)
        else:
            plt.fill(x, y, color=col, edgecolor=None)

if __name__ == "__main__":
    # Adjust start, length, max_depth and rotation as needed
    start_pos = (0.0, 0.0)
    initial_length = 1.0
    max_depth = 5
    rotation_step = 0  # degrees per recursion depth

    # Random color gradient (two random RGB colors)
    def random_color():
        return "#{:06x}".format(random.randint(0, 0xFFFFFF))
    
    color1 = mcolors.to_rgb(random_color())
    color2 = mcolors.to_rgb(random_color())

    # Clear any previous geometry, generate fractal and display it
    line_list.clear()
    triangle(start_pos, initial_length, 0, max_depth, rotation_step)
    visualize_fractal(line_list, 0, max_depth, color_start=color1, color_end=color2)

    import os

    # ensure the folder "images" exists
    os.makedirs("images", exist_ok=True)

    # save the generated fractal image
    plt.axis("off")
    plt.title("Triangle: 10 Depths, 0 Rotation")
    plt.savefig("images/fractal_triangle5.png", bbox_inches='tight', pad_inches=0)
    plt.close()
    print()