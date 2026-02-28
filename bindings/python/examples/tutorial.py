#!/usr/bin/env python3
"""
Python equivalent of examples/tutorial.cpp.
"""

import gtn


SYMBOLS = {0: "a", 1: "b", 2: "c"}
ISYMBOLS = SYMBOLS
OSYMBOLS = {0: "x", 1: "y", 2: "z"}


def simple_acceptors():
    graph = gtn.Graph()
    graph.add_node(True)
    graph.add_node(False, True)
    graph.add_node()
    graph.add_arc(0, 2, 0)
    graph.add_arc(0, 2, 1, 1)
    graph.add_arc(2, 1, 0, 0, 2.0)
    print(graph)
    gtn.draw(graph, "simple_fsa.dot", SYMBOLS)

    other = gtn.Graph()
    other.add_node(True)
    other.add_node(False, True)
    other.add_node()
    other.add_arc(0, 2, 0)
    other.add_arc(0, 2, 1, 1)
    other.add_arc(2, 1, 0, 0, 2.0)
    assert gtn.equal(graph, other)
    assert gtn.isomorphic(graph, other)


def interesting_acceptors():
    graph = gtn.Graph()
    graph.add_node(True)
    graph.add_node(True)
    graph.add_node()
    graph.add_node(False, True)
    graph.add_node(False, True)
    graph.add_arc(0, 1, 1)
    graph.add_arc(0, 2, 0)
    graph.add_arc(1, 3, 0)
    graph.add_arc(2, 3, 1)
    graph.add_arc(2, 3, 0)
    graph.add_arc(2, 4, 2)
    graph.add_arc(3, 4, 1)
    gtn.draw(graph, "multi_start_accept.dot", SYMBOLS)

    graph = gtn.Graph()
    graph.add_node(True)
    graph.add_node()
    graph.add_node(False, True)
    graph.add_arc(0, 0, 0)
    graph.add_arc(0, 1, 1)
    graph.add_arc(0, 1, 2)
    graph.add_arc(1, 2, 1)
    graph.add_arc(2, 0, 1)
    gtn.draw(graph, "cycles.dot", SYMBOLS)

    graph = gtn.Graph()
    graph.add_node(True)
    graph.add_node()
    graph.add_node(False, True)
    graph.add_arc(0, 1, 0)
    graph.add_arc(0, 1, gtn.epsilon)
    graph.add_arc(1, 2, 1)
    gtn.draw(graph, "epsilons.dot", SYMBOLS)


def simple_ops():
    g1 = gtn.Graph()
    g1.add_node(True)
    g1.add_node()
    g1.add_node(False, True)
    g1.add_arc(0, 1, 0)
    g1.add_arc(1, 2, 1)
    g1.add_arc(2, 2, 0)

    g2 = gtn.Graph()
    g2.add_node(True)
    g2.add_node()
    g2.add_node(False, True)
    g2.add_arc(0, 1, 1)
    g2.add_arc(1, 2, 0)

    g3 = gtn.Graph()
    g3.add_node(True)
    g3.add_node()
    g3.add_node(False, True)
    g3.add_arc(0, 1, 0)
    g3.add_arc(1, 2, 2)

    gtn.draw(g1, "union_g1.dot", SYMBOLS)
    gtn.draw(g2, "union_g2.dot", SYMBOLS)
    gtn.draw(g3, "union_g3.dot", SYMBOLS)
    gtn.draw(gtn.union([g1, g2, g3]), "union_graph.dot", SYMBOLS)

    gtn.draw(g2, "concat_g1.dot", SYMBOLS)
    gtn.draw(g3, "concat_g2.dot", SYMBOLS)
    gtn.draw(gtn.concat(g2, g3), "concat_graph.dot", SYMBOLS)

    g = gtn.Graph()
    g.add_node(True)
    g.add_node()
    g.add_node()
    g.add_node(False, True)
    g.add_arc(0, 1, 0)
    g.add_arc(1, 2, 1)
    g.add_arc(2, 3, 0)
    gtn.draw(g, "closure_input.dot", SYMBOLS)
    gtn.draw(gtn.closure(g), "closure_graph.dot", SYMBOLS)


def intersecting_acceptors():
    g1 = gtn.Graph()
    g1.add_node(True)
    g1.add_node(False, True)
    g1.add_arc(0, 0, 0)
    g1.add_arc(0, 1, 1)
    g1.add_arc(1, 1, 2)

    g2 = gtn.Graph()
    for i in range(4):
        g2.add_node(i == 0, i == 3)
    for src in [0, 1, 2]:
        for lab in [0, 1, 2]:
            g2.add_arc(src, src + 1, lab)

    intersected = gtn.intersect(g1, g2)
    gtn.draw(g1, "simple_intersect_g1.dot", SYMBOLS)
    gtn.draw(g2, "simple_intersect_g2.dot", SYMBOLS)
    gtn.draw(intersected, "simple_intersect.dot", SYMBOLS)


def forwarding_acceptors():
    graph = gtn.Graph()
    graph.add_node(True)
    graph.add_node(True)
    graph.add_node()
    graph.add_node(False, True)
    graph.add_arc(0, 1, 0, 0, 1.1)
    graph.add_arc(0, 2, 1, 1, 3.2)
    graph.add_arc(1, 2, 2, 2, 1.4)
    graph.add_arc(2, 3, 0, 0, 2.1)

    forwarded = gtn.forward_score(graph)
    print(f"The forward score is: {forwarded.item()}")
    gtn.draw(graph, "simple_forward.dot", SYMBOLS)

    vscore = gtn.viterbi_score(graph)
    print(f"The Viterbi score is: {vscore.item()}")
    gtn.draw(gtn.viterbi_path(graph), "simple_viterbi_path.dot", SYMBOLS)


def differentiable_acceptors():
    g1 = gtn.Graph()
    g1.add_node(True)
    g1.add_node()
    g1.add_node(False, True)
    g1.add_arc(0, 1, 0)
    g1.add_arc(0, 1, 1)
    g1.add_arc(1, 2, 0)
    g1.add_arc(1, 2, 1)

    g2 = gtn.Graph(False)
    g2.add_node(True)
    g2.add_node(False, True)
    g2.add_arc(0, 0, 0)
    g2.add_arc(0, 1, 1)

    a = gtn.forward_score(gtn.compose(g1, g2))
    b = gtn.forward_score(g1)
    loss = gtn.subtract(b, a)
    gtn.backward(loss)

    grad = g1.grad()
    for i, w in enumerate(grad.weights_to_list()):
        print(f"grad arc {i}: {w}")
    try:
        g2.grad()
    except RuntimeError as err:
        print(err)
    g1.zero_grad()


def auto_seg_criterion():
    fal = gtn.Graph()
    fal.add_node(True)
    fal.add_node()
    fal.add_node()
    fal.add_node(False, True)
    fal.add_arc(0, 1, 0)
    fal.add_arc(1, 1, 0)
    fal.add_arc(1, 2, 1)
    fal.add_arc(2, 2, 1)
    fal.add_arc(2, 3, 2)
    fal.add_arc(3, 3, 2)

    emissions = gtn.linear_graph(4, 3)
    composed = gtn.compose(fal, emissions)

    gtn.draw(fal, "asg_alignments.dot", SYMBOLS)
    gtn.draw(emissions, "asg_emissions.dot", SYMBOLS)
    gtn.draw(composed, "asg_composed.dot", SYMBOLS)

    loss = gtn.subtract(gtn.forward_score(emissions), gtn.forward_score(composed))
    gtn.backward(loss)

    transitions = gtn.Graph()
    transitions.add_node(True)
    for i in range(1, 4):
        transitions.add_node(False, True)
        transitions.add_arc(0, i, i - 1)
    for i in range(3):
        for j in range(3):
            transitions.add_arc(i + 1, j + 1, j)
    gtn.draw(transitions, "asg_transitions.dot", SYMBOLS)

    num_graph = gtn.compose(gtn.compose(fal, transitions), emissions)
    denom_graph = gtn.compose(emissions, transitions)
    gtn.subtract(gtn.forward_score(denom_graph), gtn.forward_score(num_graph))


def ctc_criterion():
    symbols = {0: "-", 1: "a", 2: "b"}

    ctc = gtn.Graph()
    for i in range(5):
        ctc.add_node(i == 0, i in (3, 4))
    ctc.add_arc(0, 0, 0)
    ctc.add_arc(0, 1, 1)
    ctc.add_arc(1, 1, 1)
    ctc.add_arc(1, 2, 0)
    ctc.add_arc(1, 3, 2)
    ctc.add_arc(2, 2, 0)
    ctc.add_arc(2, 3, 2)
    ctc.add_arc(3, 3, 2)
    ctc.add_arc(3, 4, 0)
    ctc.add_arc(4, 4, 0)

    emissions = gtn.linear_graph(4, 3)
    composed = gtn.compose(ctc, emissions)
    gtn.draw(ctc, "ctc_alignments.dot", symbols)
    gtn.draw(emissions, "ctc_emissions.dot", symbols)
    gtn.draw(composed, "ctc_composed.dot", symbols)

    gtn.subtract(gtn.forward_score(emissions), gtn.forward_score(composed))


def simple_transducers():
    graph = gtn.Graph()
    graph.add_node(True)
    graph.add_node()
    graph.add_node(False, True)
    graph.add_arc(0, 1, 0)
    graph.add_arc(0, 1, 1, 1)
    graph.add_arc(1, 2, 1, 2)
    gtn.draw(graph, "simple_fst.dot", ISYMBOLS, OSYMBOLS)


def composing_transducers():
    g1 = gtn.Graph()
    g1.add_node(True)
    g1.add_node(False, True)
    g1.add_arc(0, 0, 0, 0)
    g1.add_arc(0, 1, 1, 1)
    g1.add_arc(1, 1, 2, 2)

    g2 = gtn.Graph()
    for i in range(4):
        g2.add_node(i == 0, i == 3)
    g2.add_arc(0, 1, 0, 0)
    g2.add_arc(0, 1, 0, 1)
    g2.add_arc(0, 1, 1, 2)
    g2.add_arc(1, 2, 0, 0)
    g2.add_arc(1, 2, 1, 1)
    g2.add_arc(1, 2, 2, 2)
    g2.add_arc(2, 3, 1, 0)
    g2.add_arc(2, 3, 2, 1)
    g2.add_arc(2, 3, 2, 2)

    composed = gtn.compose(g1, g2)
    gtn.draw(g1, "transducer_compose_g1.dot", ISYMBOLS, OSYMBOLS)
    gtn.draw(g2, "transducer_compose_g2.dot", OSYMBOLS, ISYMBOLS)
    gtn.draw(composed, "transducer_compose.dot", ISYMBOLS, ISYMBOLS)


def epsilon_transitions():
    g1 = gtn.Graph()
    g1.add_node(True)
    g1.add_node()
    g1.add_node(False, True)
    g1.add_arc(0, 1, 1, gtn.epsilon, 1.1)
    g1.add_arc(1, 2, 0, 0, 2.0)
    gtn.forward_score(g1)
    g1.add_arc(0, 0, 0, gtn.epsilon, 0.5)
    gtn.draw(g1, "epsilon_graph1.dot", ISYMBOLS, OSYMBOLS)

    g2 = gtn.Graph()
    g2.add_node(True)
    g2.add_node(False, True)
    g2.add_arc(0, 1, 0, 0, 1.3)
    g2.add_arc(1, 1, gtn.epsilon, 2, 2.5)
    gtn.draw(g2, "epsilon_graph2.dot", OSYMBOLS, ISYMBOLS)

    composed = gtn.compose(g1, g2)
    gtn.draw(composed, "epsilon_composed.dot", ISYMBOLS, ISYMBOLS)


def main():
    simple_acceptors()
    interesting_acceptors()
    simple_ops()
    intersecting_acceptors()
    forwarding_acceptors()
    differentiable_acceptors()
    auto_seg_criterion()
    ctc_criterion()
    simple_transducers()
    composing_transducers()
    epsilon_transitions()


if __name__ == "__main__":
    main()
