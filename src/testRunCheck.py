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
        with open(self.output) as f:
            lines = 0
            for __ in f:
                print(__)
                lines += 1
            self.assertEqual(lines, 3)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
