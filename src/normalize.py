'''
Created on Oct 31, 2017

@author: d6fraser
'''
import unittest
import sys
import argparse


def run_normalize(in_file, out_file):
    with open(in_file) as f:
        queries = {}
        header = f.readline().strip().split(",")
        query_header = header.index("Query")
        document_header = header.index("Document")
        for line in f:
            parts = line.strip().split(",")
            print(parts)
            query_name = parts[query_header]
            document_name = parts[document_header]
            if query_name not in queries.keys():
                queries[query_name] = {}
            queries[query_name][document_name] = parts
        # now normalize all the values
        for measurement in range(header.index("Ranking") + 1, len(header)):
            for query in queries.keys():
                queries[query] = normalize_values(queries[query], measurement)
        # now output the to the other file
        with open(out_file, "w+") as h:
            print(",".join(header), file=h)
            for query in queries.keys():
                for __, values in queries[query].items():
                    temp = [str(value) for value in values]
                    print(",".join(temp), file=h)


def normalize_values(documents, measurement):
    max_value = 0
    min_value = sys.maxsize
    # find the max and min
    for document_name, values in documents.items():
        print(measurement, document_name, values)
        value = float(values[measurement])
        if value > max_value:
            max_value = value
        if value < min_value:
            min_value = value
    # now normalize those values
    for key in documents.keys():
        if min_value != max_value:
            value = float(documents[key][measurement])
            documents[key][measurement] = ((value - min_value) /
                                           (max_value - min_value))
        else:
            documents[key][measurement] = 0
    return documents


class Test(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testName(self):
        pass


if __name__ == "__main__":
    descp = "Normalize a list of values"
    parser = argparse.ArgumentParser(description=descp)
    parser.add_argument('-infile',
                        '--infile',
                        help='The path to the file to normalize',
                        required=True)
    parser.add_argument('-outfile',
                        '--outfile',
                        help='The path to the output file',
                        required=True)
    args = parser.parse_args()
    run_normalize(args.infile, args.outfile)
