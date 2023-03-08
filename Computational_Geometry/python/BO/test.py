#!/usr/bin/env python3
"""
this tests bentley ottmann on given .bo files.
for each file:
    - we display segments
    - run bentley ottmann
    - display results
    - print some statistics
"""

from bo import bentley_ottmann
from geo.segment import load_segments
from geo.point import Point


FILES = [
    'tests/carnifex_h_0.5.bo',
    'tests/fin.bo',
    'tests/flat_simple.bo',
    'tests/random_100.bo',
    'tests/random_200.bo',
    'tests/simple.bo',
    'tests/simple_three.bo',
    'tests/triangle_0.1.bo',
    'tests/triangle_0.8.bo',
    'tests/triangle_b_0.5.bo',
    'tests/triangle_b_1.0.bo',
    'tests/triangle_h_0.1.bo',
    'tests/triangle_h_0.5.bo',
    'tests/triangle_h_1.0.bo'
]

RESULTATS = [
    183,
    3,
    1,
    873,
    4527,
    1,
    3,
    97,
    16,
    46,
    14,
    175,
    34,
    15
]

def test(filename):
    """
    run bentley ottmann
    """
    adjuster, segments = load_segments(filename)
    
    # lance bentley ottmann sur les segments et l'ajusteur
    intersections = bentley_ottmann(segments, adjuster)
    list_points = [p for l in intersections for p in l]

    list_points = list(set(list_points))

    return len(list_points)


def main():
    """
    launch test on each file.
    """
    for filename, wanted in zip(FILES, RESULTATS):
        # pylint: disable=W0703
        try:
            # print(filename)
            print(filename, '\t->\t', ['FAILED', 'PASSED'][test(filename) == wanted])
        except Exception as err:
            print('=========================== FAIL ===========================')
            print('Erreur avec le fichier ', filename)
            print('erreur:', err)

main()
