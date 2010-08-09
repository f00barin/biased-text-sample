#!/usr/bin/env python
"""
Read one-sentence-per-line from stdin.
Index each line in Lucene as a separate document.

TODO:
    * Remove previous index, start from scratch.

USAGE:
    /u/turian/data/web_corpus/WaCky2/sentencesplit.py  | ./index-sentences.py

NB we use the StandardAnalyzer, but should try the SnowballAnalyzer
"""

import sys
import string
import sets

from common.stats import stats

DESIRED_NEW_DOCUMENTS_PER_ORIGINAL_DOCUMENT = 10

import lucene
from lucene import \
    SimpleFSDirectory, System, File, \
    Document, Field, StandardAnalyzer, IndexSearcher, Version, QueryParser

def retrieve(querytext, searcher, analyzer, maxresults=1000):
    query = QueryParser(Version.LUCENE_30, "text", analyzer).parse(querytext)
#    query = QueryParser(analyzer).parse("Find this sentence please")
    hits = searcher.search(query, maxresults)

#    print >> sys.stderr, "Found %d document(s) that matched query '%s':" % (hits.totalHits, query)

    for hit in hits.scoreDocs:
#        print >> sys.stderr, "\t", hit.score, hit.doc, hit.toString()
        doc = searcher.doc(hit.doc)
#        print >> sys.stderr, "\t", doc.get("text").encode("utf-8")
        yield doc.get("text")

if __name__ == "__main__":
    lucene.initVM()
    # create an index called 'index-dir' in a temp directory
#    indexDir = os.path.join(System.getProperty('java.io.tmpdir', 'tmp'),
#                            'index-dir')
    indexDir = "/Tmp/REMOVEME.index-dir"
#    indexDir = "lucene.ukwac"
    dir = SimpleFSDirectory(File(indexDir))
    analyzer = StandardAnalyzer(Version.LUCENE_30)
    searcher = IndexSearcher(dir)

    oldcorpus = sets.Set()
    newcorpus = sets.Set()

    for i, l in enumerate(open("/data/lisa5/DARPA/OpenTable/OpenTable-train-85739.ascii")):
        if i % 100 == 0:
            print >> sys.stderr, "Read %d lines from sys.stdin (newcorpus has %d documents)..." % (i, len(newcorpus))
            print >> sys.stderr, stats()
        l = l[2:]
        # Don't use duplicate sentences
        if l in oldcorpus: continue

        origcnt = len(newcorpus)
        for newl in retrieve(l, searcher, analyzer):
            # Iterate until we have added DESIRED_NEW_DOCUMENTS_PER_ORIGINAL_DOCUMENT documents
            if len(newcorpus) >= origcnt + DESIRED_NEW_DOCUMENTS_PER_ORIGINAL_DOCUMENT: break
            newcorpus.add(newl)

    for l in newcorpus:
        print l.encode("utf-8")