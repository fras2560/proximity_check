'''
Created on Oct 26, 2017

@author: d6fraser
'''
import unittest
import os
from document import Analyzer
from bs4 import BeautifulSoup
try:
    from tangent.convert import convert_math_expression
except:
    from convert import convert_math_expression


class Queries():
    def __init__(self, path):
        """Queries: the queries (arxiv format)

        Parameters:
            queries: the queries file (os.path)
        """
        with open(path) as doc:
            self.soup = BeautifulSoup(doc)
            self.queries = []
            for topic in self.soup.find_all("topic"):
                self.queries.append(Query(topic))

    def get_queries(self):
        return self.queries


class Query():
    def __init__(self, topic, analyzer=Analyzer()):
        """Query: the NTCIR-MathIR query

        Parameters:
            topic: the soup topic object (bs4)
        """
        keywords = []
        for keyword in topic.find_all("keyword"):
            for word in keyword.text.split(" "):
                keywords.append(word)
        keywords = analyzer.factory_token_filter(keywords, query=True)
        formulas = []
        for formula in topic.find_all("formula"):
            formulas += convert_math_expression(str(formula),
                                                eol=True).split(" ")
        formulas = analyzer.factory_token_filter(formulas, query=True)
        self.result = keywords + formulas
        self.name = topic.num.text
        self.result = [result for result in self.result
                       if result != ""]

    def get_terms(self):
        """Returns the clauses of the query (str)
        """
        return self.result

    def __str__(self):
        """Returns the name of the query (str)
        """
        return self.name


class Test(unittest.TestCase):
    def testInit(self):
        path = os.path.join(os.getcwd(),
                            "datasets",
                            "arxiv",
                            "NTCIR12-ArXiv.xml")
        queries = Queries(path)
        for query in queries.queries:
            print(str(query) + ":" + str(query.get_terms()))


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
