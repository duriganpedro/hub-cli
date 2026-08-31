import unittest
from hub.rag import BM25Okapi, tokenize, retrieve_top_chunks

class TestRAG(unittest.TestCase):
    def test_tokenize(self):
        text = "Hello, World! This is a test 123."
        tokens = tokenize(text)
        self.assertEqual(tokens, ["hello", "world", "this", "is", "a", "test", "123"])

    def test_bm25_empty_corpus(self):
        bm25 = BM25Okapi([])
        scores = bm25.get_scores(["test"])
        self.assertEqual(scores, [])
        self.assertEqual(retrieve_top_chunks([], "test"), [])

    def test_bm25_ranking(self):
        corpus = [
            "Python is a popular programming language.",
            "The quick brown fox jumps over the lazy dog.",
            "Programming in Python is fun and versatile.",
            "Quantum mechanics and physics formulas."
        ]
        query = "Python programming"
        results = retrieve_top_chunks(corpus, query, top_k=2)
        self.assertEqual(len(results), 2)
        self.assertIn("Programming in Python is fun and versatile.", results)
        self.assertIn("Python is a popular programming language.", results)
        self.assertNotIn("Quantum mechanics and physics formulas.", results)

    def test_bm25_no_matches(self):
        corpus = ["Apples and oranges", "Bananas and grapes"]
        results = retrieve_top_chunks(corpus, "robotics space", top_k=2)
        self.assertEqual(results, [])

if __name__ == "__main__":
    unittest.main()
