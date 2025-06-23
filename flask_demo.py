## In the terminal, "export FLASK_APP=flask_demo" (without .py)
## flask run -h 0.0.0.0 -p 8888
## http://localhost:8888/input


import lucene
import os
from org.apache.lucene.store import MMapDirectory, SimpleFSDirectory, NIOFSDirectory
from java.nio.file import Paths
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.index import FieldInfo, IndexWriter, IndexWriterConfig, IndexOptions, DirectoryReader
from org.apache.lucene.search import IndexSearcher, BoostQuery, Query
from org.apache.lucene.search.similarities import BM25Similarity
from reddit_search.search import search_index
from flask import request, Flask, render_template

app = Flask(__name__)

sample_doc = [
    {
        'title' : 'A',
        'context' : 'lucene is a useful tool for searching and information retrieval'
        },
    {
        'title' : 'B',
        'context' : 'Bert is a deep learning transformer model for encoding textual data'
    },
    {
        'title' : 'C',
        'context' : 'Django is a python web framework for building backend web APIs'
    }
]      

def retrieve(storedir, query, method="bm25"):
    lucene.getVMEnv().attachCurrentThread()

    results = search_index(storedir, query_str=query, field="selftext", top_k=10,method=method)
    
    
    topkdocs = []
    
    for score, doc in results:
        selftext = doc.get("selftext") or ""
        truncated_text = selftext[:300]
        topkdocs.append({
            "score": round(score, 2),
            "title": doc.get("title"),
            "text": truncated_text
        })
        
    return topkdocs
    #print(topkdocs)

@app.route("/")
def home():
    return 'huh'

@app.route("/abc")
def abc():
    return 'hello alien'

@app.route('/input', methods = ['POST', 'GET'])
def input():
    return render_template('input.html')

@app.route('/output', methods = ['POST', 'GET'])
def output():
    if request.method == 'GET':
        return f"Nothing"
    if request.method == 'POST':
        form_data = request.form
        query = form_data['query']
        method = form_data.get('method', 'bm25')
        print(f"this is the query: {query}")
        lucene.getVMEnv().attachCurrentThread()
        docs = retrieve('reddit_search/reddit_index/', str(query), method)
        print(docs)

        print("Query:", query)
        print("Docs retrieved:", docs)
        
        return render_template('output.html',lucene_output = docs)
    
if not lucene.getVMEnv():
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])

    
if __name__ == "__main__":
    app.run(debug=True)

# create_index('sample_lucene_index/')
# retrieve('sample_lucene_index/', 'web data')
