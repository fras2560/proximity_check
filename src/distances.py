'''
Created on Oct 26, 2017

@author: d6fraser
'''
import unittest


def calculate_distances(query, tf_dictionary):
    positions = []
    for term in query.get_terms():
        try:
            positions.append(tf_dictionary[term])
        except KeyError:
            pass
    # remove any terms that are not present
    positions = [pos for pos in positions if len(pos) > 0]
    pairs = calculate_pairs(positions)
    span_distance = span(positions)
    min_span_distance = min_span(positions)
    return (span_distance,
            min_span_distance,
            span_distance / sum([len(pos) for pos in positions]),
            min_span_distance / len(positions),
            min(pairs),
            average_pairs(pairs),
            max(pairs)
            )


def calculate_pairs(positions):
    pairs = []
    for index, position in enumerate(positions):
        for pos in position:
            pairs += [abs(pos - pos2)
                      for term in positions[index+1:]
                      for pos2 in term]
    return pairs


def average_pairs(pairs):
    return sum(pairs) / len(pairs)


def span(positions):
    smallest_position = min([min(pos) for pos in positions])
    largest_position = max([max(pos) for pos in positions])
    return largest_position - smallest_position


def remove_lower_positions(positions, lower):
    new_positions = []
    for position in positions:
        new_positions.append([pos for pos in position if pos >= lower])
    return new_positions


def min_span(positions):
    spans = []
    start = 0
    end = max([max(pos) for pos in positions])
    while start < end:
        try:
            span_start = min([min(pos) for pos in positions])
            span_end = max([min(pos) for pos in positions])
            spans.append(abs(span_end - span_start))
            start = span_start + 1
            positions = remove_lower_positions(positions, start)
        except ValueError:
            start = end
    return min(spans)


class QueryMock():
    def __init__(self, terms):
        self.terms = terms

    def get_terms(self):
        return self.terms


class TestCalculateDistance(unittest.TestCase):
    def setUp(self):
        self.q = QueryMock(["a", "b", "c"])
        self.d = {"a": [1, 2],
                  "b": [3, 4],
                  "c": [5, 6]}

    def testCalculateDistances(self):
        (s, m, ns, nm, sd, ad, lr) = calculate_distances(self.q, self.d)
        self.assertEquals(s, 5)
        self.assertEquals(m, 3)
        self.assertEquals(ns, 5 / 6)
        self.assertEquals(nm, 3 / 3)
        self.assertEquals(sd, 1)
        self.assertEquals(ad, 8 / 3)
        self.assertEquals(lr, 5)


class TestBasicFunctions(unittest.TestCase):
    def setUp(self):
        self.pos1 = [[0, 2, 4, 6],
                     [1, 4, 7],
                     [2, 4, 6]]
        self.pos2 = [[1, 7],
                     [2, 6],
                     [5]]
        self.pos3 = [[1, 7],
                     [2, 6],
                     [3, 4, 5]]

    def testMinSpan(self):
        self.assertEquals(min_span(self.pos1), 0)
        self.assertEquals(min_span(self.pos2), 2)
        self.assertEquals(min_span(self.pos3), 2)

    def testSpan(self):
        self.assertEquals(span(self.pos1), 7)
        self.assertEquals(span(self.pos2), 6)
        self.assertEquals(span(self.pos3), 6)

    def testCalcPairs(self):
        expect = [1, 4, 7, 2, 4, 6, 1, 2, 5, 0, 2, 4, 3, 0, 3, 2, 0, 2, 5, 2,
                  1, 4, 2, 0, 1, 3, 5, 2, 0, 2, 5, 3, 1]
        self.assertEquals(calculate_pairs(self.pos1), expect)
        expect = [1, 5, 4, 5, 1, 2, 3, 1]
        self.assertEquals(calculate_pairs(self.pos2), expect)
        expect = [1, 5, 2, 3, 4, 5, 1, 4, 3, 2, 1, 2, 3, 3, 2, 1]
        self.assertEquals(calculate_pairs(self.pos3), expect)

    def testAveragePair(self):
        self.assertEqual(average_pairs([1, 2, 3]), 2)
        self.assertEqual(average_pairs([4, 2, 6]), 4)



if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()