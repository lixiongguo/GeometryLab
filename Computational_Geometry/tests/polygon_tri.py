import matplotlib.pyplot as plt
import numpy as np
import random
from shapely.geometry import Polygon, LinearRing #多边形模型，和线性环模型

def IsSimplePoly(poly):
    """判断多边形poly是否为简单多边形"""
    poly_ring = poly.boundary
    if poly_ring.is_ring and list(poly.interiors) == []:
        return True
    else:
        return False
def GetPolyVex(poly):
    """得到poly的顶点序列，以numpy数组的形式返回
       :首尾点重合，该数组为n*2的数组
    """
    return np.asarray(poly.exterior.coords)
def VexCCW(poly):
    """判断poly的顶点给出的是顺时针顺序还是逆时针顺序
       :若给出的顶点为逆时针排列则返回1，为顺时针旋转则返回-1
    """
    return 1 if LinearRing(poly.exterior).is_ccw else -1
def GetDivideVexIdx(poly):
    """得到poly中的可划分顶点的下标序列
         :返回1，无重复顶点np数组，顺序与poly.exterior中的顺序相同
         :返回2，其中可划分顶点的下标序列
         :返回3，可划分顶点的多在角的弧度序列
    """
    dividevex_idx_li = [] #存储可划分顶点的下标
    dividevex_arg_li = [] #存储可划分顶点所对应角的弧度值
    vex_arr = GetPolyVex(poly) #顶点序列
    vex_arr = vex_arr[:-1,:] #去掉最后一个回环
    nums = vex_arr.shape[0] #顶点序列的个数
    if nums <= 3: #三角形则不用再处理
        return vex_arr, dividevex_idx_li, dividevex_arg_li
    
    pm = VexCCW(poly) #poly的顺逆时针状态
    for i in range(nums):
        v = vex_arr[i,:]#当前顶点
        l = vex_arr[i-1,:]#前驱顶点
        r = vex_arr[(i+1)%nums,:]#后继顶点
        fir_vector = v - l #用有向面积法计算是否为凸顶点
        sec_vector = r - v
        A = np.array([fir_vector,sec_vector]) #判断矩阵
        if pm*np.linalg.det(A) > 0:#此时的顶点为凸顶点，在此基础上判断其是否为可划分顶点
            remainvex_arr = np.concatenate([vex_arr[:i,:],vex_arr[i+1:,:]],axis=0)
            remain_poly = Polygon(remainvex_arr)
            tri = Polygon([l,v,r])
            if (remain_poly.is_valid
                and remain_poly.intersection(tri).area < 1e-8 #为一个可调整系数
                and poly.equals(remain_poly.union(tri))):#判断一个凸顶点是否为可划分顶点的依据
                
                dividevex_idx_li.append(i) #将可划分的顶点下标压入序列
                #下面计算对应的弧度
                arc = np.arccos(-np.dot(fir_vector,sec_vector)/np.linalg.norm(fir_vector)/np.linalg.norm(sec_vector))
                dividevex_arg_li.append(arc)
    return vex_arr, dividevex_idx_li, dividevex_arg_li
def GetDivTri(poly, tris = []):
    """递归的将多边形，进行三角剖分，每次都以角度最小的可划分顶点为依据"""
    vex_arr, dv_idx_li, dv_arc_li = GetDivideVexIdx(poly)
    nums = vex_arr.shape[0]
    if nums <= 3: #三角形，则直接处理
        tris.append(poly)
        return tris
    idx = dv_idx_li[np.argmin(np.array(dv_arc_li))]#取出最小的一个可划分顶点的下标
    #idx = dv_idx_li[np.random.randint(len(dv_idx_li))]#随机取出一个下标
    v = vex_arr[idx, :]
    l = vex_arr[idx-1, :]
    r = vex_arr[(idx+1)%nums, :]
    tri = Polygon([l,v,r]) #划分出来的三角形
    tris.append(tri) #将这个处理好的三角形压入序列
    #下面为得到新序列，并转化为图形，用于递归
    remain_vex_arr = np.concatenate([vex_arr[:idx,:],vex_arr[idx+1:,:]],axis=0)
    remain_poly = Polygon(remain_vex_arr)
    GetDivTri(remain_poly,tris)
    return tris
def PolyPretreatment(poly_arr):
    """用于对poly_arr进行归一化处理"""
    temp = poly_arr - np.min(poly_arr,axis=0)
    return temp / np.max(temp)
def MinAngle(tri):
    """计算一个三角形的最小角的弧度[0,pi/2]"""
    point = np.asarray(tri.exterior.coords)
    arc_li = []
    for i in range(3):
        j = (i+1)%3; k=(i+2)%3
        a = np.linalg.norm(point[i,:] - point[j,:])
        b = np.linalg.norm(point[j,:] - point[k,:])
        c = np.linalg.norm(point[k,:] - point[i,:])
        arc = np.arccos((a**2 + b**2 - c**2)/(2*a*b))
        arc_li.append(arc)
    return min(arc_li)
def OptDiv(poly4_vex_arr):
    """对四边形进行优化划分，返回其最优化的两个三角形"""
    tri1 = Polygon(poly4_vex_arr[[0,1,2]])
    tri2 = Polygon(poly4_vex_arr[[0,2,3]])
    arc1 = min([MinAngle(tri1),MinAngle(tri2)])

    tri3 = Polygon(poly4_vex_arr[[0,1,3]])
    tri4 = Polygon(poly4_vex_arr[[1,2,3]])
    arc2 = min([MinAngle(tri3),MinAngle(tri4)])

    if arc1 >= arc2:
        return tri1,tri2
    else:
        return tri3,tri4
def OptAlltris(tris):
    """对已经给出的三角剖分进行进一步的优化，使得最小角最大
        :对剖分出的三角形序列进行优化
        :通常需要运行两次，才能保证充分优化
    """
    random.shuffle(tris)
    nums = len(tris)
    for i in range(nums):
        tri_i = tris[i]
        for j in range(i+1,nums):
            tri_j = tris[j]
            if tri_i.intersection(tri_j).length > 1e-10:
                u = tri_i.union(tri_j)
                vex_arr, dv_vex_li, _=GetDivideVexIdx(u)
                if len(dv_vex_li) == 4:
                    a,b = OptDiv(vex_arr)
                    flag = True
                    for idx in set(range(nums)) - {i,j}:
                        if a.intersection(tris[idx]).area > 0. or b.intersection(tris[idx]).area > 0.:
                            flag = False
                    if flag:
                        tris[i],tris[j] = a,b
    return tris
##-----------------------------------------------##
poly_arr = np.array([(0,0),(1,2),(0,4),(3,6),(2,5),(3,5),(4,3),(0,0)]) #顶点序列
poly = Polygon(PolyPretreatment(poly_arr)) #构造多边形
#运算,绘图脚本
if IsSimplePoly(poly):
    plt.figure(figsize=(16,16))
    tris = []
    tris =  GetDivTri(poly,tris = tris)
    #用mpl画出，原来图形的线框
    plt.subplot(2,2,1)
    plt.plot(*poly.exterior.xy)
    plt.axis("equal")
    #用线框画出剖分
    plt.subplot(2,2,2)
    for tri in tris: #triangulate得到的所有三角形，这是对凸包的一个划分
        plt.plot(*tri.exterior.xy)
    plt.axis("equal")
    #用色块画出剖分
    plt.subplot(2,2,3)
    for tri in tris:
        color = np.random.rand(4)
        color[3] *= 0.6#以下两句用于调节透明度
        color[3] += 0.4
        tri = plt.Polygon(np.asarray(tri.exterior.coords),facecolor = color)
        plt.gca().add_patch(tri)
    #进行优化，并用色块画出新的剖分
    newtris = tris.copy()
    newtris = OptAlltris(newtris) # 进行优化
    newtris = OptAlltris(newtris)
    plt.subplot(2,2,4)
    for tri in newtris:
        color = np.random.rand(4)
        color[3] *= 0.6#以下两句用于调节透明度
        color[3] += 0.4
        tri = plt.Polygon(np.asarray(tri.exterior.coords),facecolor = color)
        plt.gca().add_patch(tri)
        

    plt.show()
else:
     print("输入的多边形，不是定义要求的简单多边形！")
