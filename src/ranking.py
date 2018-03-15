'''
Created on Oct 31, 2017

@author: d6fraser
'''
import unittest
import argparse
K_VALUES = [1, 2, 3]
RELEVANT = ["RELEVANT", "PARTIALLY RELEVANT"]


def run_ranking(in_file, out_file):
    with open(in_file) as f:
        queries = {}
        header = f.readline().strip().split(",")
        query_header = header.index("Query")
        document_header = header.index("Document")
        relevant_header = header.index("Ranking")
        results = {}
        # load the queries
        for line in f:
            parts = line.strip().split(",")
            print(parts)
            query_name = parts[query_header]
            document_name = parts[document_header]
            if query_name not in queries.keys():
                queries[query_name] = {}
            queries[query_name][document_name] = parts
        # now check all measurements maps against random selecting a document
        for query in queries.keys():
            results[query] = [query]
            for measurement in range(relevant_header + 1, len(header)):
                # what are the documents
                documents = [document
                             for __, document in queries[query].items()]
                sorted_docs = sort_by_measurement(documents, measurement)
                # see how much gain versus a random selection
                ave_map = calculate_map(sorted_docs, K_VALUES, relevant_header)
                rand_map = calculate_random_map(documents,
                                                K_VALUES,
                                                relevant_header)
                info_gain = ave_map - rand_map
                print(ave_map, rand_map, info_gain)
                results[query].append(info_gain)
        # now output the to the other file
        with open(out_file, "w+") as h:
            header.pop(header.index("Document"))
            header.pop(header.index("Ranking"))
            header.pop(header.index("Doc-Length"))
            print(",".join(header), file=h)
            for query in results.keys():
                values = results[query]
                temp = [str(value) for value in values]
                print(",".join(temp), file=h)


def sort_by_measurement(documents, measurement):
    return sorted(documents, key=lambda x: x[measurement], reverse=True)


def calculate_random_map(documents, values, index):
    relevant = 0
    for parts in documents:
        if (parts[index] in RELEVANT):
            relevant += 1
    return relevant / len(documents)


def calculate_map(documents, values, index):
    total = 0
    for value in values:
        relevant = 0
        count = 0
        for parts in documents[:value]:
            if parts[index] in RELEVANT:
                relevant += 1
            count += 1
        total += relevant / count
    return total / len(values)


class Test(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testName(self):
        pass


if __name__ == "__main__":
    descp = "Rank by various measurements and check information gain"
    parser = argparse.ArgumentParser(description=descp)
    parser.add_argument('-infile',
                        '--infile',
                        help='The path to the file to rank with',
                        required=True)
    parser.add_argument('-outfile',
                        '--outfile',
                        help='The path to the output file',
                        required=True)
    args = parser.parse_args()
    run_ranking(args.infile, args.outfile)