# -*- coding: utf-8 -*-
"""Tests for the Expanding Nim manager

@author: Munir Contractor <mmc691@nyu.edu>
"""

from datetime import datetime
import os
import sys
from time import sleep
import unittest

__this_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(__this_dir + '/../')

from manager import ExpNimManager


class test_manager(unittest.TestCase):

    def test_plain(self):
        manager = ExpNimManager(16, 2)
        move = manager.move(0, 2, 0)
        self.assertFalse(move['finished'])
        self.assertEqual(move['current_max'], 3)
        move = manager.move(1, 3, 0)
        self.assertFalse(move['finished'])
        self.assertEqual(move['current_max'], 4)
        move = manager.move(0, 2, 1)
        self.assertFalse(move['finished'])
        self.assertEqual(move['current_max'], 3)
        self.assertEqual(move['player_0']['resets_left'], 1)
        move = manager.move(1, 3, 1)
        self.assertFalse(move['finished'])
        self.assertEqual(move['current_max'], 3)
        self.assertEqual(move['player_0']['resets_left'], 1)
        move = manager.move(0, 3, 1)
        self.assertFalse(move['finished'])
        self.assertEqual(move['current_max'], 3)
        self.assertEqual(move['player_0']['resets_left'], 0)
        move = manager.move(1, 2, 0)
        self.assertFalse(move['finished'])
        self.assertEqual(move['current_max'], 4)
        move = manager.move(0, 1, 0)
        self.assertTrue(move['finished'])

    def test_out_of_turn(self):
        manager = ExpNimManager(6, 1)
        move = manager.move(0, 2, 0)
        self.assertFalse(move['finished'])
        self.assertEqual(move['current_max'], 3)
        move = manager.move(0, 2, 0)
        self.assertTrue(move['finished'])
        self.assertEqual(move['winner'], '1')
        self.assertIn('out of turn', move['reason'])

    def test_legal_reset(self):
        manager = ExpNimManager(10, 1)
        move = manager.move(0, 3, 0)
        self.assertFalse(move['finished'])
        self.assertEqual(move['player_0']['resets_left'], 1)
        self.assertEqual(move['current_max'], 4)
        move = manager.move(1, 4, 0)
        self.assertFalse(move['finished'])
        self.assertEqual(move['current_max'], 5)
        move = manager.move(0, 2, True)
        self.assertFalse(move['finished'])
        self.assertEqual(move['player_0']['resets_left'], 0)
        self.assertEqual(move['current_max'], 3)

    def test_illegal_reset(self):
        manager = ExpNimManager(10, 1)
        move = manager.move(0, 3, 1)
        self.assertFalse(move['finished'])
        self.assertEqual(move['player_0']['resets_left'], 0)
        self.assertEqual(move['current_max'], 3)
        move = manager.move(1, 3, 0)
        self.assertFalse(move['finished'])
        self.assertEqual(move['current_max'], 4)
        move = manager.move(0, 2, True)
        self.assertTrue(move['finished'])
        self.assertIn('too many resets', move['reason'])

    def test_timeout(self):
        manager = ExpNimManager(10, 1, game_time=2)
        manager.players[0].prev_time = datetime.now()
        sleep(1)
        move = manager.move(0, 2, 0)
        sleep(2)
        move = manager.move(1, 3, 1)
        self.assertTrue(move['finished'])
        self.assertIn('time limit', move['reason'])
        self.assertEqual(move['winner'], '0')

    def test_timeout_first_turn(self):
        manager = ExpNimManager(10, 1, game_time=1)
        manager.players[0].prev_time = datetime.now()
        sleep(2)
        move = manager.move(0, 3, 0)
        self.assertTrue(move['finished'])
        self.assertIn('time limit', move['reason'])
        self.assertEqual(move['winner'], '1')

    def test_current_max(self):
        manager = ExpNimManager(32, 1)
        move = manager.move(0, 3, 0)
        self.assertEqual(move['current_max'], 4)
        move = manager.move(1, 4, 0)
        self.assertEqual(move['current_max'], 5)
        move = manager.move(0, 2, 0)
        self.assertEqual(move['current_max'], 5)
        move = manager.move(1, 5, 1)
        self.assertEqual(move['current_max'], 3)
        move = manager.move(0, 3, 0)
        self.assertEqual(move['current_max'], 6)
        move = manager.move(1, 4, 0)
        self.assertEqual(move['current_max'], 6)
        move = manager.move(0, 5, 1)
        self.assertEqual(move['current_max'], 3)

    def test_current_max2(self):
        manager = ExpNimManager(16, 1)
        move = manager.move(0, 2, 1)
        self.assertEqual(move['current_max'], 3)
        move = manager.move(1, 3, 0)
        self.assertEqual(move['current_max'], 4)


if __name__ == '__main__':
    unittest.main(exit=False)
