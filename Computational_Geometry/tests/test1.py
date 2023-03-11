import tkinter

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

import numpy as np


root = tkinter.Tk()
root.wm_title("Embedding in Tk")

np.random.seed(19680801)

fig = Figure(figsize=(5, 4), dpi=100)
canvas = FigureCanvasTkAgg(fig, master=root)  # A tk.DrawingArea.
canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

toolbar = NavigationToolbar2Tk(canvas, root)
toolbar.update()
canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)



def on_key_press(event):
    print("you pressed {}".format(event.key))
    key_press_handler(event, canvas, toolbar)


canvas.mpl_connect("key_press_event", on_key_press)


def _quit(): 
    root.quit()     # 停止主循环
    root.destroy()  # this is necessary on Windows to prevent
                    # Fatal Python Error: PyEval_RestoreThread: NULL tstate

def set_chart():
    """清除原有图表，生成新的图表"""
    global fig,canvas
    fig.clear()

    # 计算颜色和面积
    N = 150
    r = 2 * np.random.rand(N)
    theta = 2 * np.pi * np.random.rand(N)
    area = 200 * r**2
    colors = theta
    ax = fig.add_subplot(111, projection='polar')
    ax.scatter(theta, r, c=colors, s=area, cmap='hsv', alpha=0.75)
    canvas.draw()

# 生成并显示图表
set_chart()

frm_1 = tkinter.Frame(master=root)             
button = tkinter.Button(master=frm_1, text="Change", command=set_chart)
button.pack(side=tkinter.LEFT)

button = tkinter.Button(master=frm_1, text="Quit", command=_quit)
button.pack(side=tkinter.RIGHT)
frm_1.pack(side=tkinter.BOTTOM)

tkinter.mainloop()
