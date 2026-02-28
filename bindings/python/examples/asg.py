#!/usr/bin/env python3
"""
ASG example ported from examples/asg.cpp.
"""

import gtn


def main():
    # Input length and target
    n = 27
    t = 5
    output = [2, 0, 19]  # "c", "a", "t"
    l = len(output)

    emissions = gtn.linear_graph(t, n)

    transitions = gtn.Graph()
    transitions.add_node(True)
    for i in range(1, n + 1):
        transitions.add_node(False, True)
        transitions.add_arc(0, i, i - 1)  # p(i | <s>)
    for i in range(n):
        for j in range(n):
            transitions.add_arc(i + 1, j + 1, j)  # p(j | i)

    fal = gtn.Graph()
    fal.add_node(True)
    for idx, label in enumerate(output, start=1):
        fal.add_node(False, idx == l)
        fal.add_arc(idx, idx, label)
        fal.add_arc(idx - 1, idx, label)

    fal_alignments = gtn.compose(emissions, gtn.compose(fal, transitions))
    fal_score = gtn.forward_score(fal_alignments)

    fcc_alignments = gtn.compose(emissions, transitions)
    fcc_score = gtn.forward_score(fcc_alignments)

    asg_score = gtn.subtract(fcc_score, fal_score)

    print(
        f"FAL Alignments Graph Nodes: {fal_alignments.num_nodes()} "
        f"Arcs: {fal_alignments.num_arcs()} (should be {(2 * l - 1) * (t - l) + l})"
    )
    print(
        f"FCC Alignments Graph Nodes: {fcc_alignments.num_nodes()} "
        f"Arcs: {fcc_alignments.num_arcs()} (should be {n * n * (t - 1) + n})"
    )
    print(f"FAL Score: {fal_score.item()}")
    print(f"FCC Score: {fcc_score.item()}")
    print(f"ASG Score: {asg_score.item()}")

    gtn.backward(asg_score)


if __name__ == "__main__":
    main()
