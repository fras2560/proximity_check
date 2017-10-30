'''
Created on Oct 26, 2017

@author: d6fraser
'''
from queries import Queries
from results import Results
from document import Document, Analyzer
from distances import calculate_distances
from tqdm import tqdm
import os
import argparse


def run_check(output_file,
              documents,
              queries,
              results,
              ext=".xhtml",
              formula_bags=False,
              keep_words=True,
              keep_math=True
              ):
    """Calculates 7 different proximity distance measurements and outputs
    the results to a file

    Parameters:
        output_file: the file to output to
        documents: a path to the folder containing all the documents
        queries: a file with all the queries (see NTCIR format)
        results: a file with the relevance for each query
        ext: the extension of the files in documents
        formula_bags: whether to treat formulas as bags of words
        keep_words: whether to keep the words or not
        keep_math: whether to keep the math formulas or not
    """
    with open(output_file, "w+") as out:
        analyzer = Analyzer(formula_bags=formula_bags,
                            keep_words=keep_words,
                            keep_math=keep_math)
        queries = Queries(queries).get_queries()
        results = Results(results)
        print("{},{},{},{},{},{},{},{},{}".format("Query",
                                                  "Document",
                                                  "Ranking",
                                                  "Span",
                                                  "Min-Span",
                                                  "Normalized-Span",
                                                  "Normalized-Min-Span",
                                                  "Min-Distance",
                                                  "Ave-Distance",
                                                  "Max-Distance"), file=out)
        for q in tqdm(range(0, len(queries))):
            query = queries[q]
            for doc in results.documents_for_query(query):
                document = Document(os.path.join(documents, doc + ext))
                (tf_dic, __) = document.lookup_dictionaries(analyzer)
                dist = calculate_distances(query, tf_dic)
                relevant = lookup_relevant(results.find_score(query, doc))
                print("{},{},{},{}".format(query,
                                           document,
                                           relevant,
                                           ",".join([str(d) for d in dist])),
                      file=out)


def lookup_relevant(score):
    """Returns the string classifcation of the score"""
    category = ""
    if score >= 2.0:
        category = "RELEVANT"
    elif score > 0.0:
        category = "PARTIALLY RELEVANT"
    else:
        category = "NOT RELEVANT"
    return category


if __name__ == "__main__":
    descp = "Check the Proximity distances of the queries"
    parser = argparse.ArgumentParser(description=descp)
    parser.add_argument('-documents',
                        '--documents',
                        help='The path to the documents folder',
                        required=True)
    parser.add_argument('-queries',
                        '--queries',
                        help='The path to the queries file',
                        required=True)
    parser.add_argument("-ext",
                        "--ext",
                        help="The ext to use",
                        default=".xhtml")
    parser.add_argument('-results',
                        '--results',
                        help='The path to the results file',
                        required=True)
    parser.add_argument('-output',
                        '--output',
                        help='The path to the output file',
                        required=True)
    parser.add_argument("-formula_bags",
                        dest="formula_bags",
                        action="store_true",
                        help="Treat the formula as bags of words",
                        default=False)
    parser.add_argument("-no_math",
                        dest="no_math",
                        action="store_false",
                        help="Do not keep the math",
                        default=True)
    parser.add_argument("-no_words",
                        dest="no_words",
                        action="store_false",
                        help="Do not keep the text",
                        default=True)
    args = parser.parse_args()
    run_check(args.output,
              args.documents,
              args.queries,
              args.results,
              ext=args.ext,
              formula_bags=args.formula_bags,
              keep_words=args.no_words,
              keep_math=args.no_math)
