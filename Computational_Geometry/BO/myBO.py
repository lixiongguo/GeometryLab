import sys

from geo.segment import load_segments, Segment
from geo.tycat import tycat
from geo.point import Point
from events import init_events
from alive import Alive
from typing import List
import logging
class BaseEvent:
    def __init__(self,type:str,point:Point):
        self._type = type
        self._point = point

    def point(self)->Point:
        return self._point

    def type(self)->Point:
        return self._type

class IntersectEvent(BaseEvent):
    def __init__(self,point:Point,segmentA:Segment,segmentB:Segment):
        super().__init__("INT",point)
        #_segmentA左边，_segmentB右边
        self._segmentA = segmentA
        self._segmentB = segmentB

class EndEvent(BaseEvent):
    def __init__(self,point:Point,segment:Segment,type:str):
        super().__init__(type,point)
        self._segment = segment


class EventQueue:
    
    def __init__(self,segments:List[Segment]):
        self._events:List[BaseEvent]= []
        for seg in segments:
            up_point,down_point = seg.up_down_point()
            up_event = EndEvent(up_point,seg,"UP")
            down_event = EndEvent(down_point,seg,"DOWN")
            self._events.append(up_event)
            self._events.append(down_event)
        #TODO 这里应该要对同一水平线再做区分
        #lgx问题，为什么这里coordinates()会报错？
        self._events.sort(key = lambda x : x.point().coordinates[1])
        print([e.point() for e in self._events])


    def insert(self,event:IntersectEvent):
        idx = 0
        for _,e in enumerate(self._events):
            if e.point().coordinates[1] > event.point().coordinates[1]:
                break
            idx += 1
        print(len(self._events))
        print("inserting idx : ",idx)
        self._events.insert(idx,event)

        
    def is_empty(self):
        return len(self._events)<=0

    def pop(self) -> BaseEvent:
        return self._events.pop()


class BOStatus:
    
    def __init__(self):
        self._bo_status:List[Segment] = []

    def _intersect_dect(self,segA:Segment,segB:Segment)->Point:
        #TODO 学习一下这里的写法，尤其注意float的误差规避
        int_p = segA.intersection_with(segB)
        return int_p
    #lgx 事件可能是[[],[]][[],event]
    #算法高效的一个重要原因是只跟周边对比
    def _check(self,idx,flag):
        events = []
        print(self._bo_status,idx)
        seg  = self._bo_status[idx]
        if idx > 0 and flag&1:
            pointA = self._intersect_dect(self._bo_status[idx-1],seg)
            if pointA:
                eventA = IntersectEvent(pointA,self._bo_status[idx-1],seg)
                events.append(eventA)
        if idx < len(self._bo_status)-1 and flag&2:
            pointB = self._intersect_dect(self._bo_status[idx+1],seg)
            if pointB:
                eventB = IntersectEvent(pointB,seg,self._bo_status[idx+1])
                events.append(eventB)
        return events

    def insert(self,seg:Segment)->IntersectEvent:
        idx = 0
        for i,seg_i in enumerate(self._bo_status):
            if seg.left_x() < seg_i.left_x():
                idx = i
                break
        self._bo_status.insert(idx,seg)
        events = self._check(idx,3)
        return events
    #lgx会不会有反复加入事件点导致重复添加事件的情况？
    #调换也要check
    def switch(self,event:IntersectEvent):
        #Find Intersect Event
        events = []
        idx = 0
        print("Change before",self._bo_status)
        for idx,seg in enumerate(self._bo_status):
            if seg == event._segmentA:
                a_idx = idx
            if seg == event._segmentB:
                b_idx = idx
        #这里只能是相邻的
        assert b_idx - a_idx == 1  
        self._bo_status[a_idx] = event._segmentB
        self._bo_status[b_idx] = event._segmentA
        print("Change after",self._bo_status)
        #只能跟前面比，与只能跟后面比
        events.extend(self._check(a_idx,1))
        events.extend(self._check(b_idx,2))
        return events

    #退出也要check
    def pop(self,seg:Segment):
        events = []
        idx = 0
        for i,seg_i in enumerate(self._bo_status):
            if seg_i == seg:
                idx = i
                break
        self._bo_status.pop(idx)
        if self._bo_status is None:
             #退出之后，后面一个填上跟前一个比
            event = self._check(idx,1)
            events.extend(event)
            return events
       
        
class lgx_BO:

    def __init__(self,segments : List[Segment]):
        self._bo_status = BOStatus()
        self._event_queue = EventQueue(segments)
        self._results = []

    def bo_solve(self):
        while not self._event_queue.is_empty():
            event = self._event_queue.pop()
            events:List[BaseEvent]= []
            #debug
            print(f"Poping {event.point()},{event.type()}")
            if event._type == "UP":
                events = self._bo_status.insert(event._segment)
            elif event._type == "INT":
                events = self._bo_status.switch(event)
            else :
                events = self._bo_status.pop(event._segment)
            if events is not None:
                for event in events:
                    if event is None:
                        continue
                    print(f"Inserting {event.point()},{event.type()}")
                    self._event_queue.insert(event)
                    self._results.append(event._point)
        print(self._results)
        return self._results        
        
