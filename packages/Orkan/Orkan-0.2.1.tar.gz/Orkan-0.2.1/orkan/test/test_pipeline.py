import random
import unittest

from orkan import Pipeline


def s(callback):
    """Simple spout that puts some random numbers into the Pipeline."""
    for _ in range(10):
        n = int(random.random() * 1000000)
        callback(n)


def b1(n):
    """Simple bolt that doubles the passed element (via return)."""
    return n * 2


def b2(n, callback):
    """Simple bolt that halves the passed element (via callback)."""
    callback(n / 2)


def v(n, callback):
    """Simple bolt for an inifinte stream of incoming data, that
    prints the result at the end of the Pipeline and does not pass
    anything on."""
    print n


TEST_RUNS = 1


class PipelineTests(unittest.TestCase):

    def test_non_parallel_pipeline(self):
        for _ in range(TEST_RUNS):
            pipeline = Pipeline([(s, 1)], [(b1, 1), (b2, 1)])
            results = list(pipeline.start(n_jobs=1))
            self.assertEqual(len(results), 10)

    def test_parallel_pipeline(self):
        for _ in range(TEST_RUNS):
            pipeline = Pipeline([(s, 1)], [(b1, 1), (b2, 1)])
            results = list(pipeline.start(n_jobs=3))
            self.assertEqual(len(results), 10)

    def test_parallel_workers(self):
        for _ in range(TEST_RUNS):
            pipeline = Pipeline([(s, 1)], [(b1, 2), (b2, 1)])
            results = list(pipeline.start(n_jobs=4))
            self.assertEqual(len(results), 10)

    def test_more_workers_than_processes(self):
        for _ in range(TEST_RUNS):
            pipeline = Pipeline([(s, 2)], [(b1, 2), (b2, 2)])
            results = list(pipeline.start(n_jobs=4))
            self.assertEqual(len(results), 20)

    def test_no_result(self):
        for _ in range(TEST_RUNS):
            pipeline = Pipeline([(s, 1)], [(b1, 1), (v, 1)])
            results = list(pipeline.start(n_jobs=4))
            self.assertEqual(results, [])


if __name__ == '__main__':
    unittest.main()
