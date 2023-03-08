"""
This module provide an object to manage alive segments of the bentley ottmann algorithm
"""

from bisect import bisect_left
from geo.segment import Segment
from geo.point import Point

from sortedcontainers import SortedList

WITH_SORTED_LIST = False

class Alive:
    """
    This object store the segments and manage the insertion, suppression,
    and keep sorted the list with the function traiter_intersection
    """
    def __init__(self):
        # pylint: disable=R0204
        # operation are only done with the correct object
        if WITH_SORTED_LIST:
            self.list = SortedList()
        else:
            self.list = []

    def iter_segments(self, mini=None, maxi=None):
        """
        iterate on segments presents on the alive list between the points mini and maxi
        if mini or maxi is not set, it takes plus or minus infinity
        """
        if mini is None:
            mini = float('-inf')
        if maxi is None:
            maxi = float('inf')


        #pylint: disable=C0103
        # y is the ordinate of the scan point
        y = Segment.scanPoint.coordinates[1]
        i = bisect_left(self.list, Segment([Point([mini-0.001, y]), Point([mini-0.001, y-1])]))
        j = bisect_left(self.list, Segment([Point([maxi+0.001, y]), Point([maxi+0.001, y-1])]))
        for index in range(i, j):
            yield self.list[index]

    def ajouter_alive(self, segment):
        """
        Add the segment in the alive list, it is inserted at the correct place with its key
        """
        if WITH_SORTED_LIST:
            self.list.add(segment)
            i = self.list.index(segment)
        else:
            i = bisect_left(self.list, segment)
            self.list.insert(i, segment)

        right, left = None, None
        if i > 0:
            left = self.list[i-1]
        if i < len(self.list)-1:
            right = self.list[i+1]

        return left, right

    def retirer_alive(self, segment):
        """
        Remove the segments from the alive list
        """

        if WITH_SORTED_LIST:
            i = self.list.index(segment)
        else:
            i = bisect_left(self.list, segment)

        right, left = None, None
        if i > 0:
            left = self.list[i-1]
        if i < len(self.list)-1:
            right = self.list[i+1]

        if right and left:
            assert left <= right

        assert segment == self.list[i], "L'élément n'est pas dans la liste (ou non trouvé)"
        self.list.pop(i)


        return left, right

    def check_sort(self):
        """
        DEBUG function
        to check if the list is correctly sorted
        raise an exception if the list is not sorted
        """
        if self.list == []:
            return True
        seg_iter = iter(self.list)
        last = next(seg_iter)
        for segment in seg_iter:
            if last > segment:
                raise Exception('non trié')
            last = segment
        return True
