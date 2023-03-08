import tkinter

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np


root = tkinter.Tk()
root.wm_title("Embedding in Tk")

fig = plt.figure()
ax = fig.add_subplot(111)
ax.set_xlim([0, 10])
ax.set_ylim([0, 10])

canvas = FigureCanvasTkAgg(fig, master=root)  # A tk.DrawingArea.
canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)




li_feasible_points = []

def write_data():
    global li_feasible_points
    if(len(li_feasible_points) > 2):
        line = plt.Polygon(li_feasible_points, closed=True, color='r', fill=False, edgecolor='r')
        plt.gca().add_line(line)
    canvas.draw()

def _quit(): 
    root.quit()     # 停止主循环
    root.destroy()

def onclick(event):
    if event.xdata and event.ydata:
        global fig,ax,canvas
        global li_feasible_points
        li_feasible_points.append([event.xdata, event.ydata])
        ax.scatter(event.xdata, event.ydata, s=10, c='r')
        canvas.draw()

fig.canvas.mpl_connect('button_press_event', onclick)

frm_1 = tkinter.Frame(master=root)             
button = tkinter.Button(master=frm_1, text="Write", command=write_data)
button.pack(side=tkinter.LEFT)

button = tkinter.Button(master=frm_1, text="Quit", command=_quit)
button.pack(side=tkinter.RIGHT)
frm_1.pack(side=tkinter.BOTTOM)
tkinter.mainloop()
