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
        doc_length_header = header.index("Doc-Length")
        # build up the
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
                queries[query] = normalize_values(queries[query],
                                                  measurement,
                                                  doc_length_header)
        # now output the to the other file
        with open(out_file, "w+") as h:
            print(",".join(header), file=h)
            for query in queries.keys():
                for __, values in queries[query].items():
                    temp = [str(value) for value in values]
                    print(",".join(temp), file=h)


def normalize_values(documents, measurement, doc_length_index):
    # normalize by doc length
    for key in documents.keys():
        value = float(documents[key][measurement])
        doc_length = float(documents[key][doc_length_index]
        documents[key][measurement] = value / doc_length
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
