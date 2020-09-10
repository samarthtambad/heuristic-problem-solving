# -*- coding: utf-8 -*-
"""This file contains a regression test for the game to make
sure that client and server are working as expected
"""

import json
import multiprocessing
from multiprocessing.pool import ThreadPool
import os
import sys
import time
import traceback
import unittest

__this_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(__this_dir + '/../')

from client import Client
from manager import ExpNimManager


class Process(multiprocessing.Process):

    def __init__(self, *args, **kwargs):
        multiprocessing.Process.__init__(self, *args, **kwargs)
        self._pconn, self._cconn = multiprocessing.Pipe()
        self._exception = None

    def run(self):
        try:
            multiprocessing.Process.run(self)
            self._cconn.send(None)
        except Exception as e:
            tb = traceback.format_exc()
            self._cconn.send((e, tb))
            raise

    @property
    def exception(self):
        if self._pconn.poll():
            self._exception = self._pconn.recv()
        return self._exception


class test_client_server(unittest.TestCase):

    address = '127.0.0.1'

    def __create_client(self, name, reset, address, port):
        return Client(name, reset, (address, port))

    def set_up(self, port):
        self.manager = ExpNimManager(8, 1, address=self.address,
                                     port=port)
        self.p = Process(target=self.manager.run_game)
        self.p.start()
        time.sleep(1)
        pool = ThreadPool()
        async_create = pool.apply_async(self.__create_client,
                                        ('foo 1', False, self.address, port))
        self.client0 = Client('foo 0', True, (self.address, port))
        self.client1 = async_create.get()

    def tear_down(self):
        self.p.terminate()
        self.client0.close()
        self.client1.close()

    def test_simple(self):
        self.set_up(9000)
        moves = []
        opp_moves = []
        moves.append(self.client0.make_move(2))
        opp_moves.append(self.client1.receive_move())
        self.assertEqual(moves[0]['stones_removed'], 2)
        self.assertEqual(moves[0]['reset_used'], False)
        self.assertFalse(moves[0]['finished'])
        self.assertEqual(moves[0]['current_max'], 3)
        self.assertEqual(moves[0]['stones_left'], 6)
        self.assertEqual(moves[0], opp_moves[0])
        moves.append(self.client1.make_move(3, True))
        opp_moves.append(self.client0.receive_move())
        self.assertEqual(moves[1]['stones_removed'], 3)
        self.assertEqual(moves[1]['reset_used'], True)
        self.assertFalse(moves[1]['finished'])
        self.assertEqual(moves[1]['current_max'], 3)
        self.assertEqual(moves[1]['stones_left'], 3)
        self.assertEqual(moves[1], opp_moves[1])
        moves.append(self.client0.make_move(3, True))
        opp_moves.append(self.client1.receive_move())
        self.assertEqual(moves[2]['stones_removed'], 3)
        self.assertEqual(moves[2]['reset_used'], True)
        self.assertTrue(moves[2]['finished'])
        self.assertEqual(moves[2]['current_max'], 3)
        self.assertEqual(moves[2]['stones_left'], 0)
        self.assertEqual(moves[2]['winner'], 'foo 0')
        self.assertIn('won the game', moves[2]['reason'])
        self.assertEqual(moves[2], opp_moves[2])
        self.tear_down()

    def test_bad_client_order(self):
        self.set_up(9001)
        moves = []
        opp_moves = []
        moves.append(self.client0.make_move(2))
        opp_moves.append(self.client1.receive_move())
        self.assertEqual(moves[0], opp_moves[0])
        moves.append(self.client1.make_move(2))
        opp_moves.append(self.client0.receive_move())
        self.assertEqual(moves[1], opp_moves[1])
        self.client0._Client__order = 1
        moves.append(self.client0.make_move(2))
        opp_moves.append(self.client1.receive_move())
        self.assertEqual(moves[2], opp_moves[2])
        self.assertFalse(moves[2]['finished'])
        self.tear_down()


if __name__ == '__main__':
    unittest.main(exit=False)
