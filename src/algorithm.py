import numpy as np

# Define the matrices
A = np.array([
    [-1, -1, -1, 0, 0, 0],
    [1, 0, 0, -1, -1, 0],
    [0, 1, 0, 1, 0, -1],
    [0, 0, 1, 0, 1, 1]
])

B = np.array([
    [10j, 0, 0, 0, 0, 0],
    [0, 20, 0, 0, 0, 0],
    [0, 0, 30j, 0, 0, 0],
    [0, 0, 0, 40, 0, 0],
    [0, 0, 0, 0, 50j, 0],
    [0, 0, 0, 0, 0, 60]
])

C = np.array([
    [-1, 1, 0, 0],
    [-1, 0, 1, 0],
    [-1, 0, 0, 1],
    [0, -1, 1, 0],
    [0, -1, 0, 1],
    [0, 0, -1, 1]
])

# Perform the matrix multiplication
result = A @ B @ C
print(result)
