"""
Managing event module
"""

from sortedcontainers import SortedListWithKey

from geo.segment import Segment
from geo.point import Point

# Events Types
# they will be done from value max to value min
# the order is important for special cases (not present in test files)
# like intersection and start at the same point
INTERSECTION = 3    # (y, x, INTERSECTION, [segment_1, segment_2, ...])
FIN = 2             # (y, x, FIN, segment_id)
HORIZONTAL_START = 0      # (y, x, HORIZONTAL, segment_id)
HORIZONTAL_END = 4      # (y, x, HORIZONTAL, segment_id)
DEBUT = 1           # (y, x, DEBUT, segment_id)
                    # -> permet de trier les evenements selon y puis x

class Event:
    """
    Object représentant un evenement
    """
    # static variables for horizontal segment management
    current_horizontal_segment = None

    #pylint: disable=C0103
    # x and y are absiss and ordonate
    def __init__(self, y, x, evt_type, segments):
        self.y = y
        self.x = x
        self.evt_type = evt_type
        if not isinstance(segments, list):
            segments = [segments]
        self.segments = segments

    def __lt__(self, other):
        return (self.y, self.x, self.evt_type) < \
               (other.y, other.x, other.evt_type)

    def __eq__(self, other):
        return (self.y, self.x, self.evt_type, self.segments) == \
               (other.y, other.x, other.evt_type, other.segments)

    def traiter_evenement(self, intersections, events, alive_list, adjuster):
        """
        Call function depending of the event type
        """
        if self.evt_type == DEBUT:
            self.start_event(events, alive_list, adjuster)

        elif self.evt_type == FIN:
            self.end_event(events, alive_list, adjuster)
            if Event.current_horizontal_segment:
                segment = self.segments[0]
                intersection_point = Point([self.x, self.y])
                intersections[segment.index].append(intersection_point)

        elif self.evt_type == HORIZONTAL_START:
            assert Event.current_horizontal_segment is None
            Event.current_horizontal_segment = self.segments[0]

        elif self.evt_type == HORIZONTAL_END:
            self.horizontal_event(alive_list, adjuster, intersections)
            Event.current_horizontal_segment = None

        elif self.evt_type == INTERSECTION:
            self.intersection_event(events, alive_list, adjuster, intersections)

        else:
            assert False, 'ERROR: unknown event code :' + self.evt_type

    def start_event(self, events, alive_list, adjuster):
        """
        Add a segment and check intersection with segments at its left anr right
        It update the scan point before the insertion
        """
        segment = self.segments[0]
        Segment.changeScanPoint(self.y, self.x)

        # Add segment to alive
        left, right = alive_list.ajouter_alive(segment)

        # check intersect between the segment and the 2 neightbour
        if left is not None:
            try_intersect(events, left, segment, adjuster)
        if right is not None:
            try_intersect(events, segment, right, adjuster)

    def end_event(self, events, alive_list, adjuster):
        """
        Remove a segment and check the intersection between the left and right neightbour
        It does not update the scan point
        """
        segment = self.segments[0]

        # remove from alive
        left, right = alive_list.retirer_alive(segment)#retirer_alive(segment)

        # check intersect between the 2 neightbour
        if left is not None and right is not None:
            try_intersect(events, left, right, adjuster)

    def intersection_event(self, events, alive_list, adjuster, intersections):
        """
        Add the intersection to the intersections object and manage the order of
        segments, and check intersections between segments
        It update the scan point
        """

        x, y, segments = self.x, self.y, self.segments
        intersection_point = Point([x, y])

        # remove segments before update alive list
        for segment in segments:
            intersections[segment.index].append(intersection_point)
            alive_list.retirer_alive(segment)

        Segment.changeScanPoint(self.y, self.x)

        # reinsert segments
        for segment in segments:
            left, right = alive_list.ajouter_alive(segment)

            if left is not None:
                try_intersect(events, left, segment, adjuster)
            if right is not None:
                try_intersect(events, segment, right, adjuster)


    def horizontal_event(self, alive_list, adjuster, intersections):
        """
        Check the intersection between the horizontal segment and alive segments
        where the segment is.
        It does not update the scan point
        """
        segment = self.segments[0]

        # check intersect between the segment and all alive
        [xmin, xmax] = [e.coordinates[0] for e in segment.endpoints]
        [xmin, xmax] = [xmin, xmax] if xmin <= xmax else [xmax, xmin]

        for segment_2 in alive_list.iter_segments(mini=xmin, maxi=xmax):
            intersection_point = segment.intersection_with(segment_2)
            if intersection_point:
                intersection_point = adjuster.hash_point(intersection_point)
                if intersection_point in segment.endpoints and \
                   intersection_point in segment_2.endpoints:
                    continue

                # ADDING Intersection
                intersections[segment.index].append(intersection_point)
                intersections[segment_2.index].append(intersection_point)

def try_intersect(events, segment_left, segment_right, adjuster):
    """
    Add an intersection to event if segment_left and segment_right has an intersection point
    """

    [abscisse, ordonnee] = Segment.scanPoint.coordinates

    # intersection point
    intersection_point = segment_left.intersection_with(segment_right)

    if intersection_point:
        intersection_point = adjuster.hash_point(intersection_point)

        # if the intersection is a the extremity of the two segments, ignore it
        if intersection_point in segment_left.endpoints and \
           intersection_point in segment_right.endpoints:
            return

        # we have a correct intersection point
        [x_i, y_i] = intersection_point.coordinates

        # we add the event if it is in the future
        if y_i < ordonnee or (y_i == ordonnee and x_i < abscisse):

            event = Event(y_i, x_i, INTERSECTION, [segment_left, segment_right])

            # we add the segment to the segments of the event or we add it
            try:
                i = events.index(event)
                segments = events[i].segments
                if not segment_left in segments:
                    segments.add(segment_left)
                if not segment_right in segments:
                    segments.add(segment_right)
            except ValueError:
                events.add(event)


def init_events(segments):
    """
    Initialize the event object with begining and ending events of segments
    """
    # Creation of starting, ending and horizontal events
    events = SortedListWithKey(key=lambda e: (e.y, e.x, e.evt_type))

    for segment in segments:
        [start_point, end_point] = segment.endpoints
        [start, end] = [p.coordinates[1] for p in segment.endpoints]

        # start point at the bottom (y go to the bottom => bottom :: greater)
        if start < end:
            start, end = end, start
            start_point, end_point = end_point, start_point

        y_max = start

        if end == start:
            # special case for horizontal segments
            x_min = min(start_point.coordinates[0], end_point.coordinates[0])
            x_max = max(start_point.coordinates[0], end_point.coordinates[0])
            events.add(Event(y_max, x_min, HORIZONTAL_END, segment))
            events.add(Event(y_max, x_max, HORIZONTAL_START, segment))
        else:
            events.add(Event(y_max, start_point.coordinates[0], DEBUT, segment))
            events.add(Event(end, end_point.coordinates[0], FIN, segment))

    # Events created for segments
    return events
