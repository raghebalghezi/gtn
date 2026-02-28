#!/usr/bin/env python3
"""
Ports of examples/learned_decompositions.cpp.
"""

import gtn


def make_token_graph(label):
    g = gtn.Graph()
    g.add_node(True)
    g.add_node(False, True)
    g.add_arc(0, 1, label)
    g.add_arc(1, 1, label, gtn.epsilon)
    return g


def make_the_acceptor():
    # Accepts: t h e
    g = gtn.Graph()
    g.add_node(True)
    g.add_node()
    g.add_node()
    g.add_node(False, True)
    g.add_arc(0, 1, 2)
    g.add_arc(1, 2, 1)
    g.add_arc(2, 3, 0)
    return g


def make_the_decomposition_graph():
    # Multiple decompositions for "the".
    g = gtn.Graph()
    for i in range(4):
        g.add_node(i == 0, i == 3)
    g.add_arc(0, 1, 2, gtn.epsilon)
    g.add_arc(0, 2, 3, gtn.epsilon)
    g.add_arc(0, 3, 5, 5)
    g.add_arc(1, 2, 1, gtn.epsilon)
    g.add_arc(1, 3, 4, 5)
    g.add_arc(2, 3, 0, 5)
    return g


def asg_with_transducers():
    symbols = {0: "e", 1: "h", 2: "t"}

    e = make_token_graph(0)
    h = make_token_graph(1)
    t = make_token_graph(2)

    gtn.draw(e, "asg_e_graph.dot", symbols, symbols)
    gtn.draw(h, "asg_h_graph.dot", symbols, symbols)
    gtn.draw(t, "asg_t_graph.dot", symbols, symbols)

    tokens = gtn.closure(gtn.union([e, h, t]))
    gtn.draw(tokens, "asg_tokens.dot", symbols, symbols)

    the = make_the_acceptor()
    gtn.draw(the, "asg_simple_the.dot", symbols)

    asg_the = gtn.compose(tokens, the)
    gtn.draw(asg_the, "asg_eps_the.dot", symbols, symbols)

    asg_the = gtn.remove(asg_the, gtn.epsilon)
    gtn.draw(asg_the, "asg_fst_the.dot", symbols, symbols)

    asg_the = gtn.project_input(asg_the)
    gtn.draw(asg_the, "asg_fsa_the.dot", symbols)


def ctc_with_transducers():
    symbols = {0: "e", 1: "h", 2: "t", 3: "<B>"}

    e = make_token_graph(0)
    h = make_token_graph(1)
    t = make_token_graph(2)

    blank = gtn.Graph()
    blank.add_node(True, True)
    blank.add_arc(0, 0, 3, gtn.epsilon)
    gtn.draw(blank, "ctc_blank.dot", symbols, symbols)

    tokens = gtn.closure(gtn.union([e, h, t, blank]))
    gtn.draw(tokens, "ctc_tokens.dot", symbols, symbols)

    the = make_the_acceptor()
    ctc_the = gtn.remove(gtn.compose(tokens, the), gtn.epsilon)
    gtn.draw(ctc_the, "ctc_eps_the.dot", symbols, symbols)


def word_decompositions():
    symbols = {0: "e", 1: "h", 2: "t", 3: "th", 4: "he", 5: "the"}

    token_graphs = [make_token_graph(i) for i in range(len(symbols))]
    tokens = gtn.closure(gtn.union(token_graphs))

    the = make_the_decomposition_graph()
    gtn.draw(the, "word_decomps_the.dot", symbols, symbols)

    asg_the = gtn.remove(gtn.compose(tokens, the), gtn.epsilon)
    gtn.draw(asg_the, "asg_word_decomps_the.dot", symbols, symbols)

    symbols[6] = "<B>"
    blank = gtn.Graph()
    blank.add_node(True, True)
    blank.add_arc(0, 0, 6, gtn.epsilon)
    token_graphs.append(blank)

    tokens = gtn.closure(gtn.union(token_graphs))
    ctc_the = gtn.remove(gtn.compose(tokens, the), gtn.epsilon)
    gtn.draw(ctc_the, "ctc_word_decomps_the.dot", symbols, symbols)


def main():
    asg_with_transducers()
    ctc_with_transducers()
    word_decompositions()


if __name__ == "__main__":
    main()
