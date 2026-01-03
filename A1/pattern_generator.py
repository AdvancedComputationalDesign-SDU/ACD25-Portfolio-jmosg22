import numpy as np
import matplotlib.pyplot as plt

# array dimensions
height = 100
width = 100

# prepare canvas
canvas = np.zeros((height, width, 3), dtype=float)

# choose random colors for left and right sides (RGB vectors)
left_color  = np.random.randint(0, 256, size=3)
right_color = np.random.randint(0, 256, size=3)

# middle color = average of left and right
middle_color = (left_color + right_color) / 2

# parameters of sine wave
amplitude = 30
frequency = 4 * np.pi / height

# y-coordinates
y = np.arange(height)

# sine middle x-location for each row (shape: (height, 1))
sine_middle = (width / 2) + amplitude * np.sin(frequency * y)
sine_middle = sine_middle[:, None]   # reshape for broadcasting

# x-coordinates
x = np.arange(width)

# distance from sine middle (shape: (height, width))
distance = np.abs(x - sine_middle)

# convert distance to blending factor t (0–1)
t = distance / (width / 2)
t = np.clip(t, 0, 1)

# mask for left and right areas
left_mask  = x < sine_middle
right_mask = ~left_mask

# allocate output arrays for RGB (vectorized)
# (height, width, 1) for broadcasting with RGB vectors
t_expanded = t[..., None]

# left side fade
canvas[left_mask] = (1 - t_expanded[left_mask]) * middle_color + t_expanded[left_mask] * left_color

# right side fade
canvas[right_mask] = (1 - t_expanded[right_mask]) * middle_color + t_expanded[right_mask] * right_color

# show final image
plt.imshow(canvas.astype(np.uint8))
plt.axis("off")
plt.title("Gradient Wave Pattern")
plt.savefig("images/gradient_wavenew1.png", bbox_inches='tight', pad_inches=0)
plt.close()