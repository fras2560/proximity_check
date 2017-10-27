'''
Created on Oct 26, 2017

@author: d6fraser
'''
import os
import unittest


class Results():
    def __init__(self, document):
        """ExpectedResults: used to find the scores
                            for a document for a given query

        Parameters:
            document: the document with the queries and results
        """
        self.results = {}
        with open(document) as doc:
            for line in doc:
                parts = line.split(" ")
                if len(parts) == 4:
                    query_name = parts[0]
                    doc_name = parts[2]
                    score = parts[3]
                    if query_name not in self.results.keys():
                        self.results[query_name] = {}
                    self.results[query_name][doc_name] = float(score.strip())

    def find_score(self, query, document):
        """Returns the score for the document for a given query

        Parameters:
            query: the query object (Query)
            document: the name of the document (str)
        Returns:
            result: the resulting score, default -1 (int)
        """
        result = -1
        try:
            result = self.results[str(query)][self.parse_name(document)]
        except KeyError:
            pass
        return result

    def documents_for_query(self, query):
        result = []
        try:
            result = self.results[str(query)]
        except KeyError:
            pass
        return result

    def parse_name(self, document):
        """Returns a parse document name

        Parameters:
            document: the document name to parse (str)
        Returns:
            filename: the parse filename (str)
        """
        __, filename = os.path.split(document)
        if ".xml" in filename or ".html" in filename or "xhtml" in filename:
            filename = ".".join(filename.split(".")[0:-1])
        return filename


class Test(unittest.TestCase):
    def testInit(self):
        path = os.path.join(os.getcwd(),
                            "datasets",
                            "arxiv",
                            "NTCIR12-ArXiv-Math.dat")
        results = Results(path)
        query = "NTCIR12-MathIR-1"
        filename = "0710.3032_1_22.xml"
        self.assertEqual(results.find_score(query, filename), 1.0)
        query = "NTCIR12-MathIR-10"
        filename = "0705.0010_1_359.xml"
        self.assertEqual(results.find_score(query, filename), 2.0)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
