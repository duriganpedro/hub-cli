#!/usr/bin/env python3
import math
import re
import unicodedata
from collections import Counter

class BM25Okapi:
    def __init__(self, corpus: list[list[str]], k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.corpus = corpus
        self.doc_len = [len(doc) for doc in corpus]
        self.avgdl = sum(self.doc_len) / len(corpus) if corpus else 0
        self.doc_freqs: list[Counter] = []
        self.idf: dict[str, float] = {}
        self._initialize()

    def _initialize(self):
        df = Counter()
        for doc in self.corpus:
            frequencies = Counter(doc)
            self.doc_freqs.append(frequencies)
            for word in frequencies.keys():
                df[word] += 1
        for word, freq in df.items():
            self.idf[word] = math.log((len(self.corpus) - freq + 0.5) / (freq + 0.5) + 1)

    def get_scores(self, query: list[str]) -> list[float]:
        scores = [0.0] * len(self.corpus)
        for word in query:
            if word not in self.idf:
                continue
            idf = self.idf[word]
            for idx, doc in enumerate(self.doc_freqs):
                tf = doc.get(word, 0)
                score = idf * (tf * (self.k1 + 1)) / (tf + self.k1 * (1 - self.b + self.b * (self.doc_len[idx] / (self.avgdl or 1))))
                scores[idx] += score
        return scores

def tokenize(text: str) -> list[str]:
    norm = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8').lower()
    return re.findall(r'\w+', norm)

def retrieve_top_chunks(chunks: list[str], query: str, top_k: int = 3) -> list[str]:
    if not chunks or not query.strip():
        return []
    tokenized_corpus = [tokenize(c) for c in chunks]
    tokenized_query = tokenize(query)
    bm25 = BM25Okapi(tokenized_corpus)
    scores = bm25.get_scores(tokenized_query)
    ranked_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
    return [chunks[i] for i in ranked_indices[:top_k] if scores[i] > 0]
