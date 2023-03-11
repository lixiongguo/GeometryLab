import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import Voronoi, voronoi_plot_2d

rng = np.random.default_rng()
points = rng.random((10,2))
vor = Voronoi(points)

fig = voronoi_plot_2d(vor)
plt.show()