import cv2
import numpy as np

# Load image
image = cv2.imread("input.png", cv2.IMREAD_UNCHANGED)

# Ensure the image has an alpha channel
if image.shape[2] == 4:
    # Extract the alpha channel (transparency)
    alpha = image[:, :, 3]

    # Create a mask where the unit is visible, converting to uint8
    mask = (alpha > 0).astype(np.uint8) * 255

    # Convert to grayscale using only visible areas
    gray = cv2.cvtColor(image[:, :, :3], cv2.COLOR_BGR2GRAY)

    # Apply the mask to the grayscale image
    gray = cv2.bitwise_and(gray, gray, mask=mask)
else:
    # If no alpha channel, convert normally
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Detect edges using Canny
edges = cv2.Canny(gray, 100, 200)

# Create a transparent PNG with only the outline
transparent = np.zeros((*edges.shape, 4), dtype=np.uint8)
transparent[:, :, 0] = edges  # Red
transparent[:, :, 1] = edges  # Green
transparent[:, :, 2] = edges  # Blue
transparent[:, :, 3] = edges  # Alpha (Transparency)

# Save the output as a PNG
cv2.imwrite("unit_outline.png", transparent)
