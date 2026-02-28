#!/usr/bin/env python3
"""
Ports of examples/priors.cpp.
"""

import gtn


def build_graph(starts, accepts, arcs):
    max_node = 0
    if starts:
        max_node = max(max_node, max(starts))
    if accepts:
        max_node = max(max_node, max(accepts))
    if arcs:
        max_node = max(max_node, max(max(src, dst) for src, dst, *_ in arcs))

    g = gtn.Graph()
    for n in range(max_node + 1):
        g.add_node(n in starts, n in accepts)
    for arc in arcs:
        g.add_arc(*arc)
    return g


def asg_multi():
    symbols = {0: "e", 1: "h", 2: "t"}

    the = build_graph(
        starts={0},
        accepts={3},
        arcs=[
            (0, 0, 2),
            (0, 1, 2),
            (1, 1, 1),
            (1, 2, 1),
            (2, 2, 0),
            (2, 3, 0),
        ],
    )

    n = 3
    t = 4
    emissions = gtn.Graph()
    emissions.add_node(True)
    for frame in range(1, t + 1):
        emissions.add_node(False, frame == t)
        for label in range(n):
            emissions.add_arc(frame - 1, frame, label)

    gtn.draw(the, "asg_the.dot", symbols)
    gtn.draw(emissions, "asg_the_emissions.dot", symbols)
    gtn.draw(gtn.compose(the, emissions), "asg_the_composed.dot", symbols)

    symbols[n] = "th"
    the.add_node(True)  # node 4
    the.add_arc(4, 4, n)
    the.add_arc(4, 3, n)
    for frame in range(1, t + 1):
        emissions.add_arc(frame - 1, frame, n)

    gtn.draw(the, "asg_the_multi.dot", symbols)
    gtn.draw(emissions, "asg_the_emissions_multi.dot", symbols)
    gtn.draw(gtn.compose(the, emissions), "asg_the_composed_multi.dot", symbols)


def asg_sub_letter():
    symbols = {
        0: "-a",
        1: "-a-",
        2: "a-",
        3: "-c",
        4: "-c-",
        5: "c-",
        6: "-t",
        7: "-t-",
        8: "t-",
    }

    cat = build_graph(
        starts={0},
        accepts={6},
        arcs=[
            (0, 1, 3),
            (1, 1, 4),
            (1, 2, 5),
            (2, 3, 0),
            (3, 3, 1),
            (3, 4, 2),
            (4, 5, 6),
            (5, 5, 7),
            (5, 6, 8),
        ],
    )

    n = 9
    t = 6
    emissions = gtn.Graph()
    emissions.add_node(True)
    for frame in range(1, t + 1):
        emissions.add_node(False, frame == t)
        for label in range(n):
            emissions.add_arc(frame - 1, frame, label)

    gtn.draw(cat, "asg_cat_sub.dot", symbols)
    gtn.draw(emissions, "asg_cat_sub_emissions.dot", symbols)


def ctc_force_eps():
    symbols = {0: "-", 1: "a", 2: "c", 3: "t"}

    base = [
        (1, 1, 0),
        (1, 2, 2),
        (2, 2, 2),
        (2, 3, 0),
        (3, 3, 0),
        (2, 4, 1),
        (3, 4, 1),
        (4, 4, 1),
        (4, 5, 0),
        (5, 5, 0),
        (5, 6, 3),
        (6, 6, 3),
        (6, 7, 0),
        (7, 7, 0),
    ]

    cat = build_graph(starts={1}, accepts={6, 7}, arcs=base + [(4, 6, 3)])
    gtn.draw(cat, "ctc_cat.dot", symbols)

    cat = build_graph(starts={0}, accepts={7}, arcs=[(0, 1, 0)] + base + [(4, 6, 3)])
    gtn.draw(cat, "ctc_cat_force_start_end.dot", symbols)

    cat = build_graph(starts={1}, accepts={6, 7}, arcs=base)
    gtn.draw(cat, "ctc_cat_force_mid.dot", symbols)


def main():
    asg_multi()
    asg_sub_letter()
    ctc_force_eps()


if __name__ == "__main__":
    main()
