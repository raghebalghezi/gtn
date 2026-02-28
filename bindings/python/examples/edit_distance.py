#!/usr/bin/env python3
"""
Levenshtein distance with GTN, ported from examples/edit_distance.cpp.
"""

import gtn


def make_edits_graph(num_tokens):
    edits = gtn.Graph(False)
    edits.add_node(True, True)
    for i in range(num_tokens):
        for j in range(num_tokens):
            edits.add_arc(0, 0, i, j, -int(i != j))
        edits.add_arc(0, 0, i, gtn.epsilon, -1)  # deletion
        edits.add_arc(0, 0, gtn.epsilon, i, -1)  # insertion
    return edits


def make_chain_graph(input_tokens):
    chain = gtn.Graph(False)
    chain.add_node(True)
    for i, token in enumerate(input_tokens):
        chain.add_node(False, i == len(input_tokens) - 1)
        chain.add_arc(i, i + 1, token)
    return chain


def distance(x, y, num_tokens):
    edits = make_edits_graph(num_tokens)
    score = gtn.viterbi_score(gtn.compose(x, gtn.compose(edits, y)))
    return int(-score.item())


def main():
    num_tokens = 5
    x = make_chain_graph([0, 1, 0, 1])
    y = make_chain_graph([0, 0, 0, 1, 1])
    d = distance(x, y, num_tokens)
    assert d == 2
    print("Distance (example 1):", d)

    x = make_chain_graph([0, 1, 0, 1])
    y = make_chain_graph([0, 1, 0, 1])
    d = distance(x, y, num_tokens)
    assert d == 0
    print("Distance (example 2):", d)


if __name__ == "__main__":
    main()
