import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(111)
ax.set_xlim([0, 10])
ax.set_ylim([0, 10])

point = []
point_list = []
last_point = []
li_feasible_points = []
def onclick(event):
    # print('button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
    #       (event.button, event.x, event.y, event.xdata, event.ydata))
    # plt.plot(event.xdata, event.ydata, ',')

    # global point
    # point.clear()
    # point.extend([event.xdata, event.ydata])
    # plt.scatter(event.xdata, event.ydata, s=100, c='r')
    # global last_point
    # if last_point:
    #     plt.plot([last_point[0],point[0]],[last_point[1],point[1]])
    #     print(last_point,point)
    # last_point.clear()
    # last_point.extend([event.xdata, event.ydata])
    
    # global li_feasible_points
    # li_feasible_points.append([event.xdata, event.ydata])
    # if(len(li_feasible_points) > 2):
    #     line = plt.Polygon(li_feasible_points, closed=True, color='r', fill=False, edgecolor='r')
    #     plt.gca().add_line(line)

    global point
    point.extend([event.xdata, event.ydata])
    plt.scatter(event.xdata, event.ydata, s=10, c='r')
    if len(point) == 4:
        plt.plot([point[0],point[2]],[point[1],point[3]])
        with open('./data/line0.data','w') as f:
            str_points = [str(p) for p in point]
            str_point = ','.join(str_points)
            f.write(str_point)
        point.clear()
    fig.canvas.draw()

cid = fig.canvas.mpl_connect('button_press_event', onclick)
plt.show() 