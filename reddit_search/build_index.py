import os
import json
import lucene
from org.apache.lucene.store import SimpleFSDirectory
from java.nio.file import Paths
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.index import IndexWriter, IndexWriterConfig, IndexOptions

lucene.initVM(vmargs=['-Djava.awt.headless=true'])

INDEX_DIR = "reddit_index"
DATA_DIR = "/home/cs172/reddit_search/data/"

def create_index(index_dir, data_dir):
    if not os.path.exists(index_dir):
        os.mkdir(index_dir)
    
    store = SimpleFSDirectory(Paths.get(index_dir))
    analyzer = StandardAnalyzer()
    config = IndexWriterConfig(analyzer)
    config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
    writer = IndexWriter(store, config)

    stringType = FieldType()
    stringType.setStored(True)
    stringType.setTokenized(False)

    textType = FieldType()
    textType.setStored(True)
    textType.setTokenized(True)
    textType.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)

    total_indexed = 0

    for filename in os.listdir(data_dir):
        if filename.endswith(".json"):
            filepath = os.path.join(data_dir, filename)
            print(f"Indexing file: {filename}")
            with open(filepath, "r", encoding="utf-8") as f:
                posts = json.load(f)
                for post in posts:
                    doc = Document()
                    doc.add(Field("title", post.get("title", ""), textType))
                    doc.add(Field("selftext", post.get("selftext", ""), textType))
                    doc.add(Field("author", post.get("author", ""), stringType))
                    doc.add(Field("subreddit", post.get("subreddit", ""), stringType))
                    doc.add(Field("url", post.get("url", ""), stringType))
                    doc.add(Field("unix_time", str(post.get("unix time", "")), stringType))

                    comments_combined = " ".join(post.get("comments", []))
                    doc.add(Field("comments", comments_combined, textType))

                    writer.addDocument(doc)
                    total_indexed += 1

                    if total_indexed % 500 == 0:
                        print(f"Indexed {total_indexed} posts so far...")

    writer.close()
    print(f"\n Indexing complete. Total documents indexed: {total_indexed}")

create_index(INDEX_DIR, DATA_DIR)

