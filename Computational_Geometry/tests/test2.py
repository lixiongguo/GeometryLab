import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection

fig, ax = plt.subplots()
N=5

patches = []
r = [[0.5,0.5],
     [0.6,0.6],
     [0.7,0.8],
     [0.5,0.8],
     [0.4,0.9]
     ]
polygon = Polygon(r, True)
patches.append(polygon)

colors = 100*np.random.rand(len(patches))

p = PatchCollection(patches, alpha=0.4)
p.set_array(np.array(colors))
ax.add_collection(p)
fig.colorbar(p, ax=ax)
plt.show()
