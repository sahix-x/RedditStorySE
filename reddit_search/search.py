import lucene
import time
import math
from org.apache.lucene.store import NIOFSDirectory
from java.nio.file import Paths
from org.apache.lucene.index import Term
## Apache Lucene's query model
from org.apache.lucene.search import TermQuery, FuzzyQuery, BooleanQuery, BooleanClause
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.search import BoostQuery
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.search import IndexSearcher

if not lucene.getVMEnv():
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])

INDEX_DIR = "reddit_index"



## compute recency score used by Fuzzy Boosting
def compute_time_score(post_time, current_time=None):
    if current_time is None:

        current_time = time.time()

    ## Calculate how many hours ago the post was made.
    delta_hours = (current_time - post_time) / 3600.0


    return math.exp(-delta_hours / 24.0)

## Creates a boolean query which combines exact match query and fuzzy match query
def build_fuzzy_boosted_query(user_input, field):

    term = Term(field, user_input.lower())

    exact_query = BoostQuery(TermQuery(term), 2.0)  ## Query searches for documents that contain the exact term. Weight higher
    fuzzy_query = BoostQuery(FuzzyQuery(term, 2), 1.0)  ##Query searches for documents that contain similar to the term based on Levenshtein distance Weight lower

    combined = BooleanQuery.Builder()
    combined.add(exact_query, BooleanClause.Occur.SHOULD)
    combined.add(fuzzy_query, BooleanClause.Occur.SHOULD)

    return combined.build()




def search_index(index_dir, query_str, field="selftext", top_k=10, method = "bm25"):
    directory = NIOFSDirectory(Paths.get(index_dir))
    searcher = IndexSearcher(DirectoryReader.open(directory))
    analyzer = StandardAnalyzer()
    

    if method == "fuzzy":
        query = build_fuzzy_boosted_query(query_str, field)
    else:
        parser = QueryParser(field, analyzer)
        query = parser.parse(query_str)


    
    print(f"Searching for: {query_str} in field: {field} using {method.upper()} ranking..")
    hits = searcher.search(query, top_k).scoreDocs
    

    results = []
    for hit in hits:
        doc = searcher.doc(hit.doc)
        relevance = hit.score

        try:
            post_time = float(doc.get("unix_time"))
        except:
            post_time = 0.0

        time_score = compute_time_score(post_time)
        final_score = 0.7 * relevance + 0.3 * time_score if method == "fuzzy" else relevance 

        results.append((final_score, doc))

    results.sort(key = lambda x: x[0], reverse=True)

    return results




if __name__ == "__main__":
    while True:
        query = input("\nEnter your search query (or 'exit' to quit): ")
        if query.lower() == "exit":
            break
        field = input("Search in field (title, selftext, comments)? [default=selftext]: ") or "selftext"

        method = input("Choose ranking method (bm25/fuzzy): ").lower().strip() or "bm25"



        results = search_index(INDEX_DIR, query, field, method=method)

        for score, doc in results:
            print(f"\n--- Result (Score: {score:.2f}) ---")
            print(f"Title: {doc.get('title')}")
            print(f"Author: {doc.get('author')}")
            print(f"Subreddit: {doc.get('subreddit')}")
            print(f"URL: {doc.get('url')}")
            print(f"Time: {doc.get('unix_time')}")
            print(f"Text Snippet: {doc.get('selftext')[:300]}...")
            print("-" * 40)

