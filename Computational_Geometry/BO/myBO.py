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
        print('Intersecting-------')
        print( self._segmentA.index,self._segmentB.index)
    
    def __str__(self) -> str:
        str  = (f"({self.type()} {self._segmentA.index},{self._segmentB.index})")
        return str

class EndEvent(BaseEvent):
    def __init__(self,point:Point,segment:Segment,type:str):
        super().__init__(type,point)
        self._segment = segment
    def __str__(self) -> str:
        str  = (f"({self.type()} {self._segment.index})")
        return str


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
        self.print_events()

    def print_events(self):
        events_str = ','.join([str(e) for e in self._events])
        print('Events : %s'%events_str)

    def __str__(self) -> str:
        events_str = ','.join([str(e) for e in self._events])
        return events_str

    def insert(self,event:IntersectEvent):
        idx = 0
        while idx< len(self._events) and self._events[idx].point().coordinates[1]-0.001 < event.point().coordinates[1]:
            idx += 1
        if idx < len(self._events):
            #对比前一个避免，反复添加相同事件点
            if idx > 0 and self._events[idx-1].point().distance_to(event.point()) < 0.01:
                self._events.insert(idx,event)
            else:
                self._events.insert(idx,event)
        else:
            self._events.append(event)
        self.print_events()

        
    def is_empty(self):
        return len(self._events)<=0

    def pop(self) -> BaseEvent:
        return self._events.pop()


class BOStatus:
    
    def __init__(self):
        self._bo_status:List[Segment] = []

    def _intersect_dect(self,segA:Segment,segB:Segment,point:Point)->Point:
        #TODO 学习一下这里的写法，尤其注意float的误差规避
        int_p = segA.intersection_with(segB)
        #lgx必须要比当前事件点之后扫描到
        if int_p and int_p.coordinates[1] < point.coordinates[1]:
            return int_p

    #lgx 事件可能是[[],[]][[],event]
    #算法高效的一个重要原因是只跟周边对比
    def _check(self,idx,flag,point):
        events = []
        # self.print_bo_status('checking')
        seg  = self._bo_status[idx]
        if idx > 0 and flag&1:
            pointA = self._intersect_dect(self._bo_status[idx-1],seg,point)
            if pointA:
                eventA = IntersectEvent(pointA,self._bo_status[idx-1],seg)
                events.append(eventA)
        if idx < len(self._bo_status)-1 and flag&2:
            pointB = self._intersect_dect(self._bo_status[idx+1],seg,point)
            if pointB:
                eventB = IntersectEvent(pointB,seg,self._bo_status[idx+1])
                events.append(eventB)
        return events

    def print_bo_status(self,str_prefix):
        str_status = [status.index for status in self._bo_status]
        # print('%s:%s'%str_prefix,str_status)
        print(f"{str_prefix}:{str_status}")

    def insert(self,event:EndEvent)->IntersectEvent:
        seg =event._segment
        idx = 0
        while(idx<len(self._bo_status) and seg.up_x() > self._bo_status[idx].up_x()):
            idx += 1
        print('status inserting idx: %d'%seg.index)
        if idx < len(self._bo_status):
            self._bo_status.insert(idx,seg)
            events = self._check(idx,3,event.point())
            return events
        else:
            self._bo_status.append(seg)
            events = self._check(idx,1,event.point())
            return events
    
    #lgx会不会有反复加入事件点导致重复添加事件的情况？
    #调换也要check
    def switch(self,event:IntersectEvent):
        #Find Intersect Event
        events = []
        self.print_bo_status('Change before')
        a_idx = event._segmentA.index
        b_idx = event._segmentB.index

        #这里的a_idx,b_idx是_bo_status的idx不是segment的idx
        for idx,e_i in enumerate(self._bo_status):
            if event._segmentA.index == e_i.index:
                a_idx = idx
            if event._segmentB.index == e_i.index:
                b_idx = idx
        #这里只能是相邻的
        assert(abs(b_idx - a_idx) == 1),print(f'----------{a_idx}:{b_idx}-------{event._segmentA.index}:{event._segmentB.index}-----')
        self._bo_status[a_idx] = event._segmentB
        self._bo_status[b_idx] = event._segmentA
        self.print_bo_status('Change after')
        pre_idx = min(a_idx,b_idx)
        next_idx = max(a_idx,b_idx)
        #只能跟前面比，与只能跟后面比
        events.extend(self._check(pre_idx,1,event.point()))
        events.extend(self._check(next_idx,2,event.point()))
        return events

    #退出也要check
    def pop(self,event:EndEvent):
        seg =event._segment
        events = []
        idx = 0
        for i,seg_i in enumerate(self._bo_status):
            if seg_i.index == seg.index:
                idx = i
                break
        self.print_bo_status('Before Poping %d'%idx)
        print('%s,%s'%(seg.index,self._bo_status[idx].index))
        self.print_bo_status('After Poping %d'%idx)
        if self._bo_status and idx < len(self._bo_status):
             #退出之后，后面一个填上跟前一个比
            event = self._check(idx,1,event.point())
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
            print('Poping %s Events: %s'%(event,self._event_queue))
            if event._type == "UP":
                events = self._bo_status.insert(event)
            elif event._type == "INT":
                events = self._bo_status.switch(event)
            else :
                events = self._bo_status.pop(event)
            if events is not None:
                for event in events:
                    if event is None:
                        continue
                    print(f"Inserting {event.point()},{event.type()}")
                    self._event_queue.insert(event)
                    self._results.append(event._point)
        print(self._results)
        return self._results        
    

