import sys
import unittest
from unittest.mock import patch


class TestWatched(unittest.TestCase):
    def setUp(self):
        ...

    def tearDown(self):
        ...

    def test_args(self):
        test_args = ['prog', 'watched']
        # with patch.object(sys, 'argv', test_args):
