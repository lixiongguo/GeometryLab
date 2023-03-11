import sys

import tkinter

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from scipy.spatial import Delaunay
from scipy.spatial import ConvexHull
from scipy.spatial import KDTree
import numpy as np

root = tkinter.Tk()
root.wm_title("Embedding in Tk")

fig = plt.figure()
ax = fig.add_subplot(111)
ax.set_xlim([0, 10])
ax.set_ylim([0, 10])

canvas = FigureCanvasTkAgg(fig, master=root)  # A tk.DrawingArea.
canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)


point_list = []

def kd_query():
    global point_list
    global fig,ax,canvas
    np_point_list  = np.array(point_list)
    tree = KDTree(np_point_list)
    res = tree.query([5, 5])
    print(res,type(res))
    ax.scatter(5, 5, s=50, c='g')
    ax.scatter(res[0], res[1], s=50, c='b')
    canvas.draw()
    
def convex_hull():
   global point_list
   global fig,ax,canvas
   np_point_list  = np.array(point_list)
   hull = ConvexHull(np_point_list)
   for simplex in hull.simplices:
        ax.plot(np_point_list[simplex,0], np_point_list[simplex,1], 'k-')
   canvas.draw()

def delaunay(): 
   global point_list
   np_point_list  = np.array(point_list)
   tri = Delaunay(np_point_list)
   plt.triplot(np_point_list[:,0],np_point_list[:,1],tri.simplices)
   plt.show()

def onclick(event):
    if event.xdata and event.ydata:
        global fig,ax,canvas
        ax.scatter(event.xdata, event.ydata, s=10, c='r')
        point_list.append([event.xdata, event.ydata])
        canvas.draw()


fig.canvas.mpl_connect('button_press_event', onclick)

frm_1 = tkinter.Frame(master=root)

button = tkinter.Button(master=frm_1, text="ConvexHULL", command=convex_hull)
button.pack(side=tkinter.LEFT)

button = tkinter.Button(master=frm_1, text="Delaunay", command=delaunay)
button.pack(side=tkinter.RIGHT)

button = tkinter.Button(master=frm_1, text="KDQuery", command=kd_query)
button.pack(side=tkinter.RIGHT)

frm_1.pack(side=tkinter.BOTTOM)

tkinter.mainloop()
