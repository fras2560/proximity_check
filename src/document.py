'''
Created on Oct 26, 2017

@author: d6fraser
'''
import unittest
import os
from nltk.corpus import stopwords
try:
    from tangent.convert import convert_file_to_words, WILDCARD
except:
    from convert import convert_file_to_words, WILDCARD
from nltk.stem.porter import PorterStemmer


class Document():
    def __init__(self,
                 path):
        self.path = path
        self.words = convert_file_to_words(path,
                                           terminal_symbols=True,
                                           compound_symbols=True,
                                           expand_location=True,
                                           synonyms=True,
                                           no_payload=True)

    def __str__(self):
        return os.path.basename(self.path)

    def lookup_dictionaries(self, analyzer):
        words = analyzer.parse_words(self.words)
        tf_dict = {}
        pos_dict = {}
        for position, word in enumerate(words):
            if isinstance(word, list):
                for w in word:
                    if w in tf_dict.keys():
                        tf_dict[w].append(position)
                    else:
                        tf_dict[w] = [position]
                    if position in pos_dict.keys():
                        pos_dict[position].append(w)
                    else:
                        pos_dict[position] = [w]
            else:
                if word in tf_dict.keys():
                    tf_dict[word].append(position)
                else:
                    tf_dict[word] = [position]
                if position in pos_dict.keys():
                    pos_dict[position].append(word)
                else:
                    pos_dict[position] = [word]
        return (tf_dict, pos_dict)


class Analyzer():
    def __init__(self,
                 keep_math=True,
                 keep_words=True,
                 formula_bags=False):
        self.stemmer = PorterStemmer()
        self.keep_math = keep_math
        self.keep_words = keep_words
        self.formula_bags = formula_bags

    def parse_words(self, words):
        words = words.replace("\n", " ").replace("\r", " ")
        tokens = words.split(" ")
        tokens = self.factory_token_filter(tokens)
        return tokens

    def factory_token_filter(self, tokens, query=False):
        # make it lowercase
        tokens = self.lowercase_filter(tokens)
        # remove whitespace
        tokens = self.whitespace_filter(tokens)
        # remove punctuation
        tokens = self.punctuation_filter(tokens)
        # remove stop words
        tokens = self.stop_word_filter(tokens)
        # porter stem words
        tokens = self.porter_filter(tokens)
        # filter out math # tokens
        tokens = self.math_filter(tokens)
        if not self.keep_math:
            # remove math tags
            tokens = self.remove_math_filter(tokens)
        if not self.keep_words:
            # remove words tags
            tokens = self.remove_words_filter(tokens)
        if self.formula_bags:
            # formulas are now treated as a list
            tokens = self.formula_bag_filter(tokens)
        else:
            # tuples and their wild synonyms are saved
            tokens = self.start_end_math_tag_filter(tokens)
            if not query:
                # if not query then group them together
                tokens = self.synonym_filter(tokens)
        return tokens

    def lowercase_filter(self, tokens):
        return [token.lower() for token in tokens]

    def whitespace_filter(self, tokens):
        return [token.strip() for token in tokens
                if token.strip() != ""]

    def stop_word_filter(self, tokens):
        filtered_words = list(filter(lambda word:
                                     word not in stopwords.words('english'),
                                     tokens))
        return filtered_words

    def porter_filter(self, tokens):
        return [self.stemmer.stem(token) for token in tokens]

    def math_filter(self, tokens):
        new_tokens = []
        for token in tokens:
            if token.startswith("#") and token.endswith("#"):
                new_tokens.append(token[1:-1])
            else:
                new_tokens.append(token)
        return new_tokens

    def punctuation_filter(self, tokens):
        new_tokens = []
        for token in tokens:
            if not self.is_math_token(token):
                striped = ''.join(ch for ch in token
                                  if ch.isalnum())
                if striped.strip() != "":
                    new_tokens.append(striped)
            else:
                new_tokens.append(token)
        return new_tokens

    def remove_math_filter(self, tokens):
        new_tokens = []
        for token in tokens:
            if not self.is_math_token(token):
                new_tokens.append(token)
            else:
                new_tokens.append("(FILLER)")
        return new_tokens

    def remove_words_filter(self, tokens):
        new_tokens = []
        for token in tokens:
            if self.is_math_token(token):
                new_tokens.append(token)
            else:
                new_tokens.append("FILLER")
        return new_tokens

    def is_math_token(self, token):
        math_token = False
        if ((token.startswith("#") and token.endswith("#")) or
           (token.startswith("(") and token.endswith(")"))):
            math_token = True
        return math_token

    def formula_bag_filter(self, tokens):
        new_tokens = []
        for token in tokens:
            if token == "(start)" or token == "#(start)#":
                # used an array to store math formulas
                new_tokens.append([])
            elif token == "(end)" or token == "#(end)#":
                # do nothing
                pass
            elif (self.is_math_token(token) and
                  len(new_tokens) > 0 and
                  isinstance(new_tokens[-1], list)):
                new_tokens[-1].append(token)
            else:
                new_tokens.append(token)
        return new_tokens

    def synonym_filter(self, tokens):
        new_tokens = []
        for token in tokens:
            if "'" + WILDCARD + "'" in token:
                # it needs to be group with the other
                if (len(new_tokens) == 0):
                    new_tokens.append([token])
                elif isinstance(new_tokens[-1], list):
                    new_tokens[-1] = new_tokens[-1] + [token]
                else:
                    new_tokens[-1] = [new_tokens[-1]] + [token]
            else:
                new_tokens.append(token)
        return new_tokens

    def start_end_math_tag_filter(self, tokens):
        return [token for token in tokens
                if token != "(start)" and token != "(end)"]


class TestDocument(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testDictionaryInit(self):
        # just make sure can init the document
        Document(os.path.join(os.getcwd(), "test_files", "test.xhtml"))

    def testLookupDictionary(self):
        doc = Document(os.path.join(os.getcwd(), "test_files", "test.xhtml"))
        (tf, pos) = doc.lookup_dictionaries(Analyzer())
        expect_tf = {'mathemat': [0, 78],
                     'rigor': [1, 79],
                     'approach': [2, 81],
                     'quantum': [3, 11, 27],
                     'field': [4, 12, 28, 59, 83],
                     'theori': [5, 13, 29, 30, 60, 73, 84, 85],
                     'base': [6],
                     'oper': [7, 87],
                     'algebra': [8, 10, 26, 88],
                     'call': [9],
                     'long': [14],
                     'histori': [15],
                     'sinc': [16],
                     'pioneer': [17],
                     'work': [18, 31],
                     'araki': [19],
                     'haag': [20],
                     'kastker': [21],
                     'see': [22],
                     '22': [23],
                     'gener': [24],
                     'treatment': [25],
                     'minkowski': [32, 51],
                     'space': [33, 52],
                     'spacetim': [34, 39, 42, 54],
                     'dimens': [35],
                     'recent': [36, 65, 80],
                     'result': [37, 68],
                     'curv': [38],
                     'even': [40],
                     'noncommut': [41],
                     'case': [43],
                     "('n!1','+','n','-')": [44],
                     "('n!1','+','n')": [45],
                     "('*','+','n','-')": [45],
                     "('*','+','n')": [45],
                     "('n!1','*','n','-')": [45],
                     "('n!1','*','n')": [45],
                     "('+','n!1','n','n')": [46],
                     "('+','n!1','n')": [47],
                     "('*','n!1','n','n')": [47],
                     "('*','n!1','n')": [47],
                     "('+','*','n','n')": [47],
                     "('+','*','n')": [47],
                     "('n!1','!0','nn')": [48],
                     "('n!1','!0')": [49],
                     'dimension': [50],
                     'higher': [53],
                     'symmetri': [55, 57],
                     'conform': [56, 58, 82],
                     'seen': [61],
                     'mani': [62],
                     'new': [63],
                     'develop': [64],
                     'year': [66],
                     'survey': [67],
                     'emphasi': [69],
                     'represent': [70],
                     'theoret': [71],
                     'aspect': [72],
                     'make': [74],
                     'variou': [75],
                     'comparison': [76],
                     'anoth': [77],
                     'vertex': [86]}
        expected_posi = {0: ['mathemat'],
                         1: ['rigor'],
                         2: ['approach'],
                         3: ['quantum'],
                         4: ['field'],
                         5: ['theori'],
                         6: ['base'],
                         7: ['oper'],
                         8: ['algebra'],
                         9: ['call'],
                         10: ['algebra'],
                         11: ['quantum'],
                         12: ['field'],
                         13: ['theori'],
                         14: ['long'],
                         15: ['histori'],
                         16: ['sinc'],
                         17: ['pioneer'],
                         18: ['work'],
                         19: ['araki'],
                         20: ['haag'],
                         21: ['kastker'],
                         22: ['see'],
                         23: ['22'],
                         24: ['gener'],
                         25: ['treatment'],
                         26: ['algebra'],
                         27: ['quantum'],
                         28: ['field'],
                         29: ['theori'],
                         30: ['theori'],
                         31: ['work'],
                         32: ['minkowski'],
                         33: ['space'],
                         34: ['spacetim'],
                         35: ['dimens'],
                         36: ['recent'],
                         37: ['result'],
                         38: ['curv'],
                         39: ['spacetim'],
                         40: ['even'],
                         41: ['noncommut'],
                         42: ['spacetim'],
                         43: ['case'],
                         44: ["('n!1','+','n','-')"],
                         45: ["('n!1','+','n')",
                              "('*','+','n','-')",
                              "('*','+','n')",
                              "('n!1','*','n','-')",
                              "('n!1','*','n')"],
                         46: ["('+','n!1','n','n')"],
                         47: ["('+','n!1','n')",
                              "('*','n!1','n','n')",
                              "('*','n!1','n')",
                              "('+','*','n','n')",
                              "('+','*','n')"],
                         48: ["('n!1','!0','nn')"],
                         49: ["('n!1','!0')"],
                         50: ['dimension'],
                         51: ['minkowski'],
                         52: ['space'],
                         53: ['higher'],
                         54: ['spacetim'],
                         55: ['symmetri'],
                         56: ['conform'],
                         57: ['symmetri'],
                         58: ['conform'],
                         59: ['field'],
                         60: ['theori'],
                         61: ['seen'],
                         62: ['mani'],
                         63: ['new'],
                         64: ['develop'],
                         65: ['recent'],
                         66: ['year'],
                         67: ['survey'],
                         68: ['result'],
                         69: ['emphasi'],
                         70: ['represent'],
                         71: ['theoret'],
                         72: ['aspect'],
                         73: ['theori'],
                         74: ['make'],
                         75: ['variou'],
                         76: ['comparison'],
                         77: ['anoth'],
                         78: ['mathemat'],
                         79: ['rigor'],
                         80: ['recent'],
                         81: ['approach'],
                         82: ['conform'],
                         83: ['field'],
                         84: ['theori'],
                         85: ['theori'],
                         86: ['vertex'],
                         87: ['oper'],
                         88: ['algebra']}
        self.assertEquals(tf, expect_tf)
        self.assertEquals(pos, expected_posi)


class TestAnaylzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = Analyzer()

    def tearDown(self):
        pass

    def testPunctuationFilter(self):
        tokens = []
        self.assertEqual(self.analyzer.punctuation_filter(tokens),
                         [])
        tokens = ['is,', '-dimension', "(end)", "?"]
        expect = ['is', 'dimension', '(end)']
        self.assertEqual(self.analyzer.punctuation_filter(tokens),
                         expect)

    def testStartEndMathTagFilter(self):
        tokens = []
        self.assertEqual(self.analyzer.start_end_math_tag_filter(tokens),
                         [])
        tokens = ["(start)", "()", "(end)"]
        self.assertEqual(self.analyzer.start_end_math_tag_filter(tokens),
                         ["()"])

    def testSynonymFilter(self):
        tokens = []
        self.assertEqual(self.analyzer.synonym_filter(tokens), [])
        tokens = ["""#('v!α',"['n','b']")#""",
                  """#('*',"['n','b']")#""",
                  """#('v!α','m!()1x1','n')#""",
                  """#('*','m!()1x1','n')#""",
                  """#('v!α','*','n')#"""]
        expect = [['#(\'v!α\',"[\'n\',\'b\']")#',
                   '#(\'*\',"[\'n\',\'b\']")#'],
                  ["#('v!α','m!()1x1','n')#",
                   "#('*','m!()1x1','n')#",
                   "#('v!α','*','n')#"]]
        self.assertEqual(self.analyzer.synonym_filter(tokens), expect)
        tokens = ["""('v!α',"['n','b']")""",
                  """('*',"['n','b']")""",
                  """('v!α','m!()1x1','n')""",
                  """('*','m!()1x1','n')""",
                  """('v!α','*','n')"""]
        expect = [['(\'v!α\',"[\'n\',\'b\']")',
                   '(\'*\',"[\'n\',\'b\']")'],
                  ["('v!α','m!()1x1','n')",
                   "('*','m!()1x1','n')",
                   "('v!α','*','n')"]]
        self.assertEqual(self.analyzer.synonym_filter(tokens), expect)

    def testFormulaBagFilter(self):
        tokens = []
        self.assertEqual(self.analyzer.formula_bag_filter(tokens), [])
        tokens = ["""hey""",
                  """#(start)#""",
                  """#('v!α',"['n','b']")#""",
                  """#('*',"['n','b']")#""",
                  """#('v!α','m!()1x1','n')#""",
                  """#('*','m!()1x1','n')#""",
                  """#('v!α','*','n')#""",
                  """#(end)#""",
                  """you"""]
        expect = ['hey',
                  ['#(\'v!α\',"[\'n\',\'b\']")#',
                   '#(\'*\',"[\'n\',\'b\']")#',
                   "#('v!α','m!()1x1','n')#",
                   "#('*','m!()1x1','n')#",
                   "#('v!α','*','n')#"],
                  'you']
        self.assertEqual(self.analyzer.formula_bag_filter(tokens), expect)
        tokens = ["""hey""",
                  """(start)""",
                  """('v!α',"['n','b']")""",
                  """('*',"['n','b']")""",
                  """('v!α','m!()1x1','n')""",
                  """('*','m!()1x1','n')""",
                  """('v!α','*','n')""",
                  """(end)""",
                  """you"""]
        expect = ['hey',
                  ['(\'v!α\',"[\'n\',\'b\']")',
                   '(\'*\',"[\'n\',\'b\']")',
                   "('v!α','m!()1x1','n')",
                   "('*','m!()1x1','n')",
                   "('v!α','*','n')"],
                  'you']
        self.assertEqual(self.analyzer.formula_bag_filter(tokens), expect)

    def testIsMathToken(self):
        self.assertEqual(self.analyzer.is_math_token("""#(start)#"""), True)
        self.assertEqual(self.analyzer.is_math_token("""(start)"""), True)
        self.assertEqual(self.analyzer.is_math_token("""start"""), False)
        self.assertEqual(self.analyzer.is_math_token("""end"""), False)

    def testRemoveWordsFilter(self):
        tokens = ["""hey""",
                  """#(start)#""",
                  """#('v!α',"['n','b']")#""",
                  """#('*',"['n','b']")#""",
                  """#('v!α','m!()1x1','n')#""",
                  """#('*','m!()1x1','n')#""",
                  """#('v!α','*','n')#""",
                  """#(end)#""",
                  """you"""]
        expect = ["""FILLER""",
                  """#(start)#""",
                  """#('v!α',"['n','b']")#""",
                  """#('*',"['n','b']")#""",
                  """#('v!α','m!()1x1','n')#""",
                  """#('*','m!()1x1','n')#""",
                  """#('v!α','*','n')#""",
                  """#(end)#""",
                  """FILLER"""]
        self.assertEqual(self.analyzer.remove_words_filter(tokens), expect)

    def testRemovemathFilter(self):
        tokens = ["""hey""",
                  """#(start)#""",
                  """#('v!α',"['n','b']")#""",
                  """#('*',"['n','b']")#""",
                  """#('v!α','m!()1x1','n')#""",
                  """#('*','m!()1x1','n')#""",
                  """#('v!α','*','n')#""",
                  """#(end)#""",
                  """you"""]
        expect = ["""hey""",
                  """(FILLER)""",
                  """(FILLER)""",
                  """(FILLER)""",
                  """(FILLER)""",
                  """(FILLER)""",
                  """(FILLER)""",
                  """(FILLER)""",
                  """you"""]
        self.assertEqual(self.analyzer.remove_math_filter(tokens), expect)

    def testPorterFilter(self):
        tokens = []
        self.assertEqual(self.analyzer.porter_filter(tokens), [])
        tokens = ["arithmetic"]
        expect = ['arithmet']
        self.assertEqual(self.analyzer.porter_filter(tokens), expect)

    def testMathFilter(self):
        tokens = []
        self.assertEqual(self.analyzer.math_filter(tokens), [])
        tokens = ["""hey""",
                  """#(start)#""",
                  """#('v!α',"['n','b']")#""",
                  """#('*',"['n','b']")#""",
                  """#('v!α','m!()1x1','n')#""",
                  """#('*','m!()1x1','n')#""",
                  """#('v!α','*','n')#""",
                  """#(end)#""",
                  """you"""]
        expect = ["""hey""",
                  """(start)""",
                  """('v!α',"['n','b']")""",
                  """('*',"['n','b']")""",
                  """('v!α','m!()1x1','n')""",
                  """('*','m!()1x1','n')""",
                  """('v!α','*','n')""",
                  """(end)""",
                  """you"""]
        self.assertEqual(self.analyzer.math_filter(tokens), expect)

    def testStopWordFilter(self):
        tokens = []
        self.assertEqual(self.analyzer.stop_word_filter(tokens), [])
        tokens = ["where", "is", "the", "beef"]
        expect = ["beef"]
        self.assertEqual(self.analyzer.stop_word_filter(tokens), expect)

    def testWhiteSpaceFilter(self):
        tokens = []
        self.assertEqual(self.analyzer.whitespace_filter(tokens), [])
        tokens = [" hey",
                  " ",
                  "\n",
                  "\t",
                  "\r\n",
                  "\they"]
        expect = ["hey", "hey"]
        self.assertEqual(self.analyzer.whitespace_filter(tokens), expect)

    def testLowerCaseFilter(self):
        tokens = []
        self.assertEqual(self.analyzer.lowercase_filter(tokens), [])
        tokens = ["Wey",
                  "hey",
                  "That"]
        expect = ["wey", "hey", "that"]
        self.assertEqual(self.analyzer.lowercase_filter(tokens), expect)

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
