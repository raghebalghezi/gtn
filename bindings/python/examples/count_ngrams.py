#!/usr/bin/env python3
"""
Count n-grams with GTN, ported from examples/count_ngrams.cpp.
"""

import math

import gtn


def make_ngram_graph(n, num_tokens):
    ngram_counter = gtn.linear_graph(n, num_tokens)
    for i in range(num_tokens):
        ngram_counter.add_arc(0, 0, i, gtn.epsilon)
        ngram_counter.add_arc(n, n, i, gtn.epsilon)
    return ngram_counter


def make_chain_graph(input_tokens):
    chain = gtn.Graph(False)
    chain.add_node(True)
    for i, token in enumerate(input_tokens):
        chain.add_node(False, i == len(input_tokens) - 1)
        chain.add_arc(i, i + 1, token)
    return chain


def count_ngram(input_graph, ngram_counter, ngram_graph):
    score = gtn.forward_score(gtn.compose(input_graph, gtn.compose(ngram_counter, ngram_graph)))
    return int(round(math.exp(score.item())))


def main():
    # Toy example
    num_tokens = 2
    n = 2
    input_graph = make_chain_graph([0, 1, 0, 1])
    ngram_graph = make_chain_graph([0, 1])
    ngram_counter = make_ngram_graph(n, num_tokens)
    count = count_ngram(input_graph, ngram_counter, ngram_graph)
    assert count == 2
    print("Toy example count:", count)

    # Larger example
    num_tokens = 28
    n = 3
    ngram_counter = make_ngram_graph(n, num_tokens)
    input_graph = make_chain_graph([0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1])
    ngrams = [[0, 1, 2], [1, 2, 0], [2, 0, 1]]
    for ngram in ngrams:
        count = count_ngram(input_graph, ngram_counter, make_chain_graph(ngram))
        assert count == 3
        print(f"Count for {ngram}: {count}")


if __name__ == "__main__":
    main()
