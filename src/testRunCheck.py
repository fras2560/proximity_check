'''
Created on Oct 27, 2017

@author: d6fraser
'''
from run_check import run_check
import unittest
import os


class Test(unittest.TestCase):
    def setUp(self):
        self.file = "test.out"
        self.folder = os.path.join(os.getcwd(), "test_files")
        self.query = os.path.join(self.folder, "query.xml")
        self.result = os.path.join(self.folder, "results.txt")
        self.documents = os.path.join(self.folder, "documents")
        self.output = os.path.join(self.folder, self.file)

    def tearDown(self):
        try:
            os.remove(self.output)
        except FileNotFoundError:
            pass

    def testRunCheck(self):
        run_check(self.output,
                  self.documents,
                  self.query,
                  self.result,
                  ".html")
        expect = ["Query,Document,Doc-Length,Ranking,Span,Min-Span,Normalized-Span,Normalized-Min-Span,Min-Distance,Ave-Distance,Max-Distance",
                  "NTCIR11-Math-1,27473.html,4728,NOT RELEVANT,668,495,55.666666666666664,99.0,1,332.67857142857144,668",
                  "NTCIR11-Math-1,02459.html,1822,RELEVANT,1017,9,53.526315789473685,0.9,1,148.58333333333334,1017"]
        with open(self.output) as f:
            lines = 0
            for index, line in enumerate(f):
                self.assertEqual(expect[index].strip(), line.strip())
                lines += 1
            self.assertEqual(lines, 3)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
