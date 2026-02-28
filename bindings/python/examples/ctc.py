#!/usr/bin/env python3
"""
CTC example ported from examples/ctc.cpp.
"""

import gtn


def create_ctc_target_graph(target, blank):
    l = len(target)
    u = 2 * l + 1  # # c # a # t #
    ctc = gtn.Graph()
    for pos in range(u):
        idx = (pos - 1) // 2
        ctc.add_node(pos == 0, pos == u - 1 or pos == u - 2)
        label = target[idx] if pos % 2 else blank
        ctc.add_arc(pos, pos, label)
        if pos > 0:
            ctc.add_arc(pos - 1, pos, label)
        if pos % 2 and pos > 1 and label != target[idx - 1]:
            ctc.add_arc(pos - 2, pos, label)
    return ctc


def main():
    n = 28
    t = 5
    output = [3, 1, 20]  # "c", "a", "t"
    ctc = create_ctc_target_graph(output, blank=0)

    emissions = gtn.linear_graph(t, n)
    ctc_alignments = gtn.compose(ctc, emissions)
    ctc_loss = gtn.negate(gtn.forward_score(ctc_alignments))

    print(
        f"CTC Alignments Graph Nodes: {ctc_alignments.num_nodes()} "
        f"Arcs: {ctc_alignments.num_arcs()}"
    )
    print(f"CTC Loss: {ctc_loss.item()}")

    gtn.backward(ctc_loss)


if __name__ == "__main__":
    main()
