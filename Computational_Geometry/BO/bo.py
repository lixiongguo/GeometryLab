#!/usr/bin/env python3
"""
this tests bentley ottmann on given .bo files.
for each file:
    - we display segments
    - run bentley ottmann
    - display results
"""
import sys

from geo.segment import load_segments, Segment
from geo.tycat import tycat

from events import init_events
from alive import Alive


def bentley_ottmann_on_file(filename):
    """
    Execute the algorithm on segments presents on test files
    """
    # load segments from the file
    adjuster, segments = load_segments(filename)
    tycat(segments)
    print('Number of segments:', len(segments))

    # lance bentley ottmann sur les segments et l'ajusteur
    intersections = bentley_ottmann(segments, adjuster)
    list_points = [p for l in intersections for p in l]

    # get unique points
    list_points = list(set(list_points))

    tycat(segments, list_points)

    print("Number of unique intersection points", len(list_points))


def naive_method(segments):
    """
    Réalise le calcul d'intersection entre les segments de manière naive
    """
    from itertools import combinations
    intersect = filter(None, (c[0].intersection_with(c[1])
                              for c in combinations(segments, 2)
                              if isinstance(c[0], Segment)))
    return list(intersect)

def bentley_ottmann(segments, adjuster):
    """
    Execute the Bentley-Ottmann algorithm
    - segments is a list of Segments
    - adjuster is a coordinate hash provided by load_segments
    Return a list of intersection point for each segments
    """
    # set the adjuster to Segment object
    Segment.adjuster = adjuster

    # intersection will be in this list
    intersections = [[] for _ in segments]

    alive_list = Alive()

    # Initialize the event structure
    # It needs to have an pop(-1) method to get the last element
    events = init_events(segments)
    # Events created for segments

    # events management
    while events:
        # get the greater key (y maximal = bottom in the svg) element
        event = events.pop(-1)

        event.traiter_evenement(intersections, events, alive_list, adjuster)

    return intersections

def main():
    """
    Launch the Algorithm on files given in arguments
    The files are binary files composed by a succession of 4 points corresponding to a segment
    """
    for filename in sys.argv[1:]:
        print('test: ', filename)
        bentley_ottmann_on_file(filename)

if __name__ == '__main__':
    main()
